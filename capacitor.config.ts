import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.yuh.app',
  appName: 'YUH',
  webDir: 'out',
  server: {
    // Keep in sync with android/assets/capacitor.config.json if using live reload
    url: 'http://10.68.177.225:3000',
  },
}

export default config
