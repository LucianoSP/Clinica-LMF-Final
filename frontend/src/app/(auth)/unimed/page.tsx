'use client';

import { Dashboard } from '@/components/unimed/Dashboard';

export default function UnimedPage() {
  return (
    <div className="flex-1 space-y-6 p-6 pt-4 max-w-[1600px] mx-auto">
      <h2 className="text-3xl font-bold tracking-tight">Unimed</h2>
      <Dashboard />
    </div>
  );
}
