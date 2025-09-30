"use client"

import { useState, useEffect } from "react"
import type { ApiResponse } from "@/lib/types"

export function useApi<T>(apiCall: () => Promise<ApiResponse<T>>, dependencies: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await apiCall()

        if (isMounted) {
          if (response.success) {
            setData(response.data || null)
          } else {
            setError(response.error || "An error occurred")
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Network error")
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
    }
  }, dependencies)

  const refetch = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiCall()

      if (response.success) {
        setData(response.data || null)
      } else {
        setError(response.error || "An error occurred")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error")
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, refetch }
}

export function useMutation<T, P>(apiCall: (params: P) => Promise<ApiResponse<T>>) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mutate = async (params: P): Promise<T | null> => {
    try {
      setLoading(true)
      setError(null)

      const response = await apiCall(params)

      if (response.success) {
        return response.data || null
      } else {
        setError(response.error || "An error occurred")
        return null
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error")
      return null
    } finally {
      setLoading(false)
    }
  }

  return { mutate, loading, error }
}
