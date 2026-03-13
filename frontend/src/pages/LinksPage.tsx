import { useState } from 'react'
import { UTMBuilder } from '../components/utm/UTMBuilder'
import { UTMLinkTable } from '../components/utm/UTMLinkTable'

export function LinksPage() {
  const [showBuilder, setShowBuilder] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">UTM Links</h2>
        <button
          onClick={() => setShowBuilder(true)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Create Link
        </button>
      </div>

      <UTMLinkTable />

      {showBuilder && <UTMBuilder onClose={() => setShowBuilder(false)} />}
    </div>
  )
}
