declare module 'quagga' {
  export interface QuaggaResult {
    codeResult?: {
      code: string
    }
  }

  export interface QuaggaStatic {
    init: (config: any, callback: (err: any) => void) => void
    start: () => void
    stop: () => void
    onDetected: (callback: (result: QuaggaResult) => void) => void
  }

  const Quagga: QuaggaStatic
  export default Quagga
}