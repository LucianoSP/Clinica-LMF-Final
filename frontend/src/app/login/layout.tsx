'use client'

import { Toaster } from '@/components/ui/toaster'
// import { Toaster as SonnerToaster } from 'sonner'
import { Providers } from '../providers'

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Providers>
        {children}
        <Toaster />
        {/* <SonnerToaster position="top-center" /> */}
      </Providers>
    </div>
  )
}
