import { BarChart2, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDeleteUTMLink, useUTMLinks } from '../../hooks/useUTMLinks'
import type { UTMLink } from '../../types/utm'
import { EmptyState } from '../common/EmptyState'
import { ErrorAlert } from '../common/ErrorAlert'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { CopyButton } from './CopyButton'

const PAGE_SIZE = 20

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function LinkRow({ link }: { link: UTMLink }) {
  const { mutate: deleteLink, isPending } = useDeleteUTMLink()
  const navigate = useNavigate()
  const redirectUrl = `${window.location.origin}/r/${link.short_code}`

  return (
    <tr className="hover:bg-gray-50 border-b border-gray-100">
      <td className="px-4 py-3 text-sm font-medium text-gray-900 max-w-[200px] truncate">
        {link.title || <span className="text-gray-400 italic">Untitled</span>}
      </td>
      <td className="px-4 py-3 text-sm">
        <div className="flex items-center gap-1">
          <span className="text-indigo-600 font-mono text-xs truncate max-w-[140px]">
            {redirectUrl}
          </span>
          <CopyButton text={redirectUrl} />
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">
        {link.utm_source || <span className="text-gray-300">—</span>}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">
        {link.utm_campaign || <span className="text-gray-300">—</span>}
      </td>
      <td className="px-4 py-3 text-sm font-medium text-gray-900 text-center">
        {link.click_count.toLocaleString()}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">{formatDate(link.created_at)}</td>
      <td className="px-4 py-3 text-right">
        <div className="flex items-center justify-end gap-1">
          <button
            onClick={() => navigate(`/analytics/${link.id}`)}
            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
            title="View Analytics"
          >
            <BarChart2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => deleteLink(link.id)}
            disabled={isPending}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </td>
    </tr>
  )
}

interface UTMLinkTableProps {
  limit?: number
}

export function UTMLinkTable({ limit = PAGE_SIZE }: UTMLinkTableProps) {
  const [offset, setOffset] = useState(0)
  const { data, isLoading, error } = useUTMLinks(offset, limit)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorAlert message="Failed to load links." />
  if (!data || data.items.length === 0) {
    return (
      <EmptyState
        title="No UTM links yet"
        description="Create your first link to start tracking."
      />
    )
  }

  const totalPages = Math.ceil(data.total / limit)
  const currentPage = Math.floor(offset / limit) + 1

  return (
    <div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Title</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Short URL</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Source</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Campaign</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide text-center">Clicks</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Created</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {data.items.map((link) => (
              <LinkRow key={link.id} link={link} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm text-gray-600">
          <span>
            Page {currentPage} of {totalPages} ({data.total} total)
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= data.total}
              className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
