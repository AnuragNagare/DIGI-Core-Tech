"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import {
  ArrowLeft,
  Settings2,
  Users,
  Bell,
  Shield,
  Database,
  Info,
  Smartphone,
  Globe,
  Ruler,
  Palette,
  Volume2,
  Vibrate,
  Mail,
  Eye,
  Cookie,
  Trash2,
  Download,
  Upload,
  RotateCcw,
  HelpCircle,
  MessageSquare,
  Star,
  Coffee
} from "lucide-react"
import Link from "next/link"

interface AppSettings {
  theme: string
  language: string
  measurementUnit: string
  dateFormat: string
  timeFormat: string
  currency: string
  defaultView: string
}

interface NotificationSettings {
  pushEnabled: boolean
  emailEnabled: boolean
  smsEnabled: boolean
  expiryAlerts: boolean
  lowStockAlerts: boolean
  recipeRecommendations: boolean
  weeklyReports: boolean
  marketingEmails: boolean
  soundEnabled: boolean
  vibrationEnabled: boolean
  quietHours: boolean
  quietStart: string
  quietEnd: string
}

interface PrivacySettings {
  analytics: boolean
  crashReports: boolean
  personalizedAds: boolean
  dataSelling: boolean
  locationTracking: boolean
  cameraAccess: boolean
  storageAccess: boolean
  contactsAccess: boolean
}

interface DefaultCategories {
  produce: string
  dairy: string
  meat: string
  pantry: string
  frozen: string
  beverages: string
  snacks: string
  other: string
}

export default function SettingsPage() {
  // Settings state
  const [appSettings, setAppSettings] = useState<AppSettings>({
    theme: "light",
    language: "en",
    measurementUnit: "metric",
    dateFormat: "MM/dd/yyyy",
    timeFormat: "12h",
    currency: "USD",
    defaultView: "grid"
  })

  const [notifications, setNotifications] = useState<NotificationSettings>({
    pushEnabled: true,
    emailEnabled: true,
    smsEnabled: false,
    expiryAlerts: true,
    lowStockAlerts: true,
    recipeRecommendations: true,
    weeklyReports: false,
    marketingEmails: false,
    soundEnabled: true,
    vibrationEnabled: true,
    quietHours: false,
    quietStart: "22:00",
    quietEnd: "08:00"
  })

  const [privacy, setPrivacy] = useState<PrivacySettings>({
    analytics: true,
    crashReports: true,
    personalizedAds: false,
    dataSelling: false,
    locationTracking: false,
    cameraAccess: true,
    storageAccess: true,
    contactsAccess: false
  })

  const [categories, setCategories] = useState<DefaultCategories>({
    produce: "Fruits & Vegetables",
    dairy: "Dairy & Eggs",
    meat: "Meat & Seafood",
    pantry: "Pantry Staples",
    frozen: "Frozen Foods",
    beverages: "Beverages",
    snacks: "Snacks",
    other: "Other Items"
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm" className="p-2">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                <Settings2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                <p className="text-gray-600 text-sm">Customize your FreshKeeper experience</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-8">
          
          {/* Profile Section */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-emerald-500 to-blue-500 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Users className="w-6 h-6" />
                Profile & Account
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 bg-gradient-to-r from-emerald-400 to-blue-400 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                  U
                </div>
                <div className="flex-1 space-y-4">
                  <div>
                    <Label htmlFor="username" className="text-sm font-medium text-gray-700">Username</Label>
                    <Input id="username" defaultValue="User" className="mt-1 enhanced-input" />
                  </div>
                  <div>
                    <Label htmlFor="email" className="text-sm font-medium text-gray-700">Email</Label>
                    <Input id="email" type="email" defaultValue="user@example.com" className="mt-1 enhanced-input" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* App Preferences */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Smartphone className="w-6 h-6" />
                App Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="theme" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Palette className="w-4 h-4" />
                    Theme
                  </Label>
                  <Select value={appSettings.theme} onValueChange={(value) => setAppSettings({...appSettings, theme: value})}>
                    <SelectTrigger className="mt-1 enhanced-input">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-gray-200 shadow-xl rounded-lg">
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="language" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Globe className="w-4 h-4" />
                    Language
                  </Label>
                  <Select value={appSettings.language} onValueChange={(value) => setAppSettings({...appSettings, language: value})}>
                    <SelectTrigger className="mt-1 enhanced-input">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-gray-200 shadow-xl rounded-lg">
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="measurement" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Ruler className="w-4 h-4" />
                    Measurement Unit
                  </Label>
                  <Select value={appSettings.measurementUnit} onValueChange={(value) => setAppSettings({...appSettings, measurementUnit: value})}>
                    <SelectTrigger className="mt-1 enhanced-input">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-gray-200 shadow-xl rounded-lg">
                      <SelectItem value="metric">Metric (kg, L)</SelectItem>
                      <SelectItem value="imperial">Imperial (lb, gal)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="currency" className="text-sm font-medium text-gray-700">Currency</Label>
                  <Select value={appSettings.currency} onValueChange={(value) => setAppSettings({...appSettings, currency: value})}>
                    <SelectTrigger className="mt-1 enhanced-input">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-gray-200 shadow-xl rounded-lg">
                      <SelectItem value="USD">USD ($)</SelectItem>
                      <SelectItem value="EUR">EUR (€)</SelectItem>
                      <SelectItem value="GBP">GBP (£)</SelectItem>
                      <SelectItem value="CAD">CAD ($)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Enhanced Notifications */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Bell className="w-6 h-6" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              
              {/* Notification Types */}
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Notification Channels
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium">Push Notifications</span>
                    </div>
                    <Switch
                      checked={notifications.pushEnabled}
                      onCheckedChange={(checked) => setNotifications({...notifications, pushEnabled: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium">Email</span>
                    </div>
                    <Switch
                      checked={notifications.emailEnabled}
                      onCheckedChange={(checked) => setNotifications({...notifications, emailEnabled: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium">SMS</span>
                    </div>
                    <Switch
                      checked={notifications.smsEnabled}
                      onCheckedChange={(checked) => setNotifications({...notifications, smsEnabled: checked})}
                    />
                  </div>
                </div>
              </div>

              {/* Alert Settings */}
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Alert Settings</h4>
                <div className="space-y-3">
                  {[
                    { key: 'expiryAlerts', label: 'Expiry Alerts', desc: 'Get notified when items are about to expire' },
                    { key: 'lowStockAlerts', label: 'Low Stock Alerts', desc: 'Alert when inventory is running low' },
                    { key: 'recipeRecommendations', label: 'Recipe Suggestions', desc: 'Receive recipe recommendations based on your inventory' },
                    { key: 'weeklyReports', label: 'Weekly Reports', desc: 'Get weekly inventory and waste reports' }
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{item.label}</p>
                        <p className="text-xs text-gray-600">{item.desc}</p>
                      </div>
                      <Switch
                        checked={notifications[item.key as keyof NotificationSettings] as boolean}
                        onCheckedChange={(checked) => setNotifications({...notifications, [item.key]: checked})}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Sound & Vibration */}
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Sound & Vibration</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Volume2 className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium">Sound</span>
                    </div>
                    <Switch
                      checked={notifications.soundEnabled}
                      onCheckedChange={(checked) => setNotifications({...notifications, soundEnabled: checked})}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Vibrate className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium">Vibration</span>
                    </div>
                    <Switch
                      checked={notifications.vibrationEnabled}
                      onCheckedChange={(checked) => setNotifications({...notifications, vibrationEnabled: checked})}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Privacy & Permissions */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Shield className="w-6 h-6" />
                Privacy & Permissions
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Data Collection
                </h4>
                <div className="space-y-3">
                  {[
                    { key: 'analytics', label: 'Analytics Data', desc: 'Help us improve the app with usage analytics' },
                    { key: 'crashReports', label: 'Crash Reports', desc: 'Automatically send crash reports to help fix bugs' },
                    { key: 'personalizedAds', label: 'Personalized Ads', desc: 'Show ads based on your preferences' },
                    { key: 'dataSelling', label: 'Data Selling', desc: 'Allow selling of anonymized data to third parties' }
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{item.label}</p>
                        <p className="text-xs text-gray-600">{item.desc}</p>
                      </div>
                      <Switch
                        checked={privacy[item.key as keyof PrivacySettings] as boolean}
                        onCheckedChange={(checked) => setPrivacy({...privacy, [item.key]: checked})}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">App Permissions</h4>
                <div className="space-y-3">
                  {[
                    { key: 'cameraAccess', label: 'Camera Access', desc: 'Required for barcode scanning and receipt capture' },
                    { key: 'storageAccess', label: 'Storage Access', desc: 'Store app data and user preferences' },
                    { key: 'locationTracking', label: 'Location Tracking', desc: 'Find nearby stores and local prices' },
                    { key: 'contactsAccess', label: 'Contacts Access', desc: 'Share shopping lists with family members' }
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{item.label}</p>
                        <p className="text-xs text-gray-600">{item.desc}</p>
                      </div>
                      <Switch
                        checked={privacy[item.key as keyof PrivacySettings] as boolean}
                        onCheckedChange={(checked) => setPrivacy({...privacy, [item.key]: checked})}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Data Management */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-indigo-500 to-cyan-500 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Database className="w-6 h-6" />
                Data Management
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <Download className="w-4 h-4" />
                  Export Data
                </Button>
                
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <Upload className="w-4 h-4" />
                  Import Data
                </Button>
                
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <RotateCcw className="w-4 h-4" />
                  Reset Settings
                </Button>
                
                <Button variant="destructive" className="h-12 flex items-center gap-2">
                  <Trash2 className="w-4 h-4" />
                  Clear All Data
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* About Section */}
          <Card className="enhanced-card border-0 shadow-xl">
            <CardHeader className="bg-gradient-to-r from-gray-600 to-gray-800 text-white rounded-t-xl">
              <CardTitle className="flex items-center gap-3">
                <Info className="w-6 h-6" />
                About
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                  <Coffee className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">FreshKeeper</h3>
                  <p className="text-gray-600">Version 2.1.0</p>
                </div>
                <p className="text-sm text-gray-600 max-w-md mx-auto">
                  Your smart food inventory manager that helps reduce food waste and save money.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <HelpCircle className="w-4 h-4" />
                  Help & Support
                </Button>
                
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <MessageSquare className="w-4 h-4" />
                  Contact Us
                </Button>
                
                <Button variant="outline" className="h-12 flex items-center gap-2 enhanced-card">
                  <Star className="w-4 h-4" />
                  Rate App
                </Button>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  )
}