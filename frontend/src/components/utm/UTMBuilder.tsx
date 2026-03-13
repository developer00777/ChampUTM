import { X } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useCreateUTMLink } from '../../hooks/useUTMLinks'
import type { UTMLinkCreate } from '../../types/utm'

interface UTMBuilderProps {
  onClose: () => void
}

const INITIAL: UTMLinkCreate = {
  title: '',
  destination_url: '',
  utm_source: '',
  utm_medium: '',
  utm_campaign: '',
  utm_term: '',
  utm_content: '',
}

export function UTMBuilder({ onClose }: UTMBuilderProps) {
  const [form, setForm] = useState<UTMLinkCreate>(INITIAL)
  const { mutateAsync, isPending, error } = useCreateUTMLink()

  const previewUrl = useMemo(() => {
    if (!form.destination_url) return ''
    try {
      const url = new URL(form.destination_url)
      const params: Record<string, string> = {}
      if (form.utm_source) params.utm_source = form.utm_source
      if (form.utm_medium) params.utm_medium = form.utm_medium
      if (form.utm_campaign) params.utm_campaign = form.utm_campaign
      if (form.utm_term) params.utm_term = form.utm_term
      if (form.utm_content) params.utm_content = form.utm_content
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
      return url.toString()
    } catch {
      return form.destination_url
    }
  }, [form])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload: UTMLinkCreate = {
      ...form,
      title: form.title || undefined,
      utm_source: form.utm_source || undefined,
      utm_medium: form.utm_medium || undefined,
      utm_campaign: form.utm_campaign || undefined,
      utm_term: form.utm_term || undefined,
      utm_content: form.utm_content || undefined,
    }
    await mutateAsync(payload)
    onClose()
  }

  const set = (field: keyof UTMLinkCreate) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Create UTM Link</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title (optional)
            </label>
            <input
              type="text"
              value={form.title}
              onChange={set('title')}
              placeholder="e.g. Summer campaign email"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Destination URL <span className="text-red-500">*</span>
            </label>
            <input
              type="url"
              required
              value={form.destination_url}
              onChange={set('destination_url')}
              placeholder="https://example.com/page"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {(
              [
                ['utm_source', 'Source', 'e.g. google'],
                ['utm_medium', 'Medium', 'e.g. email'],
                ['utm_campaign', 'Campaign', 'e.g. summer_sale'],
                ['utm_term', 'Term', 'e.g. running+shoes'],
                ['utm_content', 'Content', 'e.g. logo_link'],
              ] as [keyof UTMLinkCreate, string, string][]
            ).map(([field, label, placeholder]) => (
              <div key={field} className={field === 'utm_campaign' ? 'col-span-2' : ''}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  type="text"
                  value={form[field] as string}
                  onChange={set(field)}
                  placeholder={placeholder}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            ))}
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs font-medium text-gray-500 mb-1">URL Preview</p>
              <p className="text-xs text-indigo-700 break-all font-mono">{previewUrl}</p>
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600">
              Failed to create link. Please check your input and try again.
            </p>
          )}
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isPending || !form.destination_url}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg"
          >
            {isPending ? 'Creating…' : 'Create Link'}
          </button>
        </div>
      </div>
    </div>
  )
}
