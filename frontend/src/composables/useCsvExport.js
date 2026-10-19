import { ref } from 'vue'
import api, { errText } from '../api'
import { useToast } from './useToast'

/**
 * useCsvExport
 * Handles exporting filtered dataset to CSV.
 * Uses the backend export endpoint if available (/api/:key/export/),
 * or falls back to client-side multi-page fetching with progress feedback.
 */
export function useCsvExport() {
  const exporting = ref(false)
  const progress = ref(0)
  const toast = useToast()

  async function exportCsv(resourceKey, params = {}, meta = null) {
    if (exporting.value) return
    exporting.value = true
    progress.value = 0

    const cleanParams = { ...params }
    delete cleanParams.page
    delete cleanParams.page_size

    const toastId = toast.info('Preparing CSV export…', { duration: 10000 })

    try {
      // 1. Try server-side export endpoint
      const response = await api.get(`${resourceKey}/export/`, {
        params: cleanParams,
        responseType: 'blob',
      })

      // Create download anchor
      const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const today = new Date().toISOString().slice(0, 10)
      a.href = url
      a.download = `${resourceKey}_export_${today}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      toast.success('Export completed successfully')
    } catch (e) {
      console.warn('Backend export failed or unavailable, attempting client fallback…', e)
      // 2. Client-side fallback
      try {
        await clientFallbackExport(resourceKey, cleanParams, meta)
        toast.success('Export completed successfully')
      } catch (err) {
        toast.error(`Export failed: ${errText(err)}`)
      }
    } finally {
      exporting.value = false
    }
  }

  async function clientFallbackExport(resourceKey, params, meta) {
    let allRows = []
    let page = 1
    const pageSize = 100
    const maxRows = 5000

    while (allRows.length < maxRows) {
      const resp = await api.get(`${resourceKey}/`, {
        params: { ...params, page, page_size: pageSize },
      })
      const results = resp.data.results || []
      const total = resp.data.count || 0
      allRows = allRows.concat(results)

      if (allRows.length >= total || results.length < pageSize) break
      page++
    }

    if (allRows.length === 0) {
      throw new Error('No records to export')
    }

    const columns = meta?.columns || Object.keys(allRows[0])
    const headers = columns.map((c) => meta?.fields?.[c]?.label || c)

    const csvLines = [headers.join(',')]
    for (const row of allRows) {
      const line = columns.map((c) => {
        let val = row[`${c}_label`] !== undefined ? row[`${c}_label`] : row[c]
        if (val === null || val === undefined) val = ''
        if (typeof val === 'object') val = JSON.stringify(val)
        val = String(val).replace(/"/g, '""')
        return `"${val}"`
      })
      csvLines.push(line.join(','))
    }

    const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${resourceKey}_export_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return {
    exporting,
    progress,
    exportCsv,
  }
}
