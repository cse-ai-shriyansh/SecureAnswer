import Card from '../components/Card'
import Button from '../components/Button'
import { Play, Copy, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { runRetrieval } from '../lib/api'

export default function RetrievalDebug() {
  const [question, setQuestion] = useState('')
  const [expandedChunk, setExpandedChunk] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [chunks, setChunks] = useState([])

  const handleQuery = () => {
    if (!question.trim()) return
    setIsLoading(true)
    runRetrieval(question, { top_k: 5 })
      .then((res) => {
        const results = res.retrieval_chunks || res.context_chunks || []
        const formatted = results.map((chunk) => ({
          id: `${chunk.doc_id}#${chunk.chunk_id}`,
          source: chunk.source_file || chunk.doc_id,
          preview: chunk.chunk_text?.substring(0, 100) + '...' || 'N/A',
          text: chunk.chunk_text || '',
          score: chunk.score || chunk.combined_score || 0,
        }))
        setChunks(formatted)
        console.debug('retrieval result', formatted)
      })
      .catch((e) => {
        console.error('Retrieval failed:', e)
        setChunks([])
      })
      .finally(() => setIsLoading(false))
  }

  const getSimilarityColor = (score) => {
    if (typeof score !== 'number') return 'bg-gray-100 text-text-secondary'
    if (score >= 0.9) return 'bg-green-100 text-green-700'
    if (score >= 0.8) return 'bg-blue-100 text-blue-700'
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-700'
    return 'bg-orange-100 text-orange-700'
  }

  return (
    <div className="space-y-8">
      {/* Query Input */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Debug Retrieval</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Enter your question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={4}
              className="w-full p-4 border border-border rounded-md bg-bg-primary text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth resize-none"
              placeholder="Ask your question..."
            />
          </div>
          <div className="flex gap-3">
            <Button variant="primary" onClick={handleQuery} disabled={isLoading}>
              <Play size={18} className="inline mr-2" />
              {isLoading ? 'Retrieving...' : 'Retrieve Chunks'}
            </Button>
            <Button variant="secondary" onClick={() => navigator.clipboard.writeText(question)}>
              <Copy size={18} />
            </Button>
          </div>
        </div>
      </Card>

      {/* Retrieved Chunks */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">
          Retrieved Chunks ({chunks.length})
        </h3>
        <div className="space-y-3">
          {chunks.map((chunk) => (
            <div
              key={chunk.id}
              className="border border-border rounded-md overflow-hidden transition-smooth hover:border-primary"
            >
              <div
                onClick={() =>
                  setExpandedChunk(expandedChunk === chunk.id ? null : chunk.id)
                }
                className="p-4 cursor-pointer hover:bg-bg-primary transition-smooth flex items-center justify-between"
              >
                <div className="flex-1 flex items-start gap-4">
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-semibold text-center flex-shrink-0 ${getSimilarityColor(
                      chunk.score
                    )}`}
                  >
                    {(chunk.score * 100).toFixed(0)}%
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary">{chunk.source}</p>
                    <p className="text-sm text-text-secondary mt-1">{chunk.preview}</p>
                  </div>
                </div>
                {expandedChunk === chunk.id ? (
                  <ChevronUp size={20} className="text-text-secondary flex-shrink-0" />
                ) : (
                  <ChevronDown size={20} className="text-text-secondary flex-shrink-0" />
                )}
              </div>

              {/* Expanded content */}
              {expandedChunk === chunk.id && (
                <div className="px-4 py-4 bg-bg-primary border-t border-border">
                  <p className="text-sm text-text-primary leading-relaxed">{chunk.text}</p>
                  <div className="mt-4 flex items-center gap-2">
                    <span className="text-xs text-text-secondary">Similarity Score:</span>
                    <div className="flex-1 max-w-xs bg-border rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-smooth"
                        style={{ width: `${chunk.score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-medium text-primary">
                      {(chunk.score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <p className="text-xs uppercase tracking-[0.2em] text-text-secondary mb-2">Live retrieval</p>
        <p className="text-sm text-text-secondary">
          Retrieval settings are controlled by the backend and the current query. This page only shows actual returned chunks.
        </p>
      </Card>
    </div>
  )
}
