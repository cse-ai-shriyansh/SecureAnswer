 
 import Card from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { Send, Copy, ThumbsUp, ThumbsDown, Lightbulb } from 'lucide-react'
import { useState, startTransition } from 'react'
import { generateAnswer } from '../lib/api'

export default function AnswerGeneration() {
  const [question, setQuestion] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedAnswer, setGeneratedAnswer] = useState(null)
  const [citations, setCitations] = useState([])
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!question.trim()) {
      setError('Please enter a question before generating an answer.')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const res = await generateAnswer({ question, use_llm: true })
      const retrievalChunks = Array.isArray(res.retrieval_chunks) ? res.retrieval_chunks : []

      startTransition(() => {
        setGeneratedAnswer({
          text: res.answer || 'Insufficient evidence',
          confidence: res.confidence ?? 0,
          generationTime: `${res.generation_mode === 'llm' ? 'LLM' : 'Extractive'}${res.llm_enabled ? ' connected' : ' fallback'}`,
          hallucinationRisk: Boolean(res.hallucination_risk),
          retrievalConfidence: res.retrieval_confidence ?? 0,
        })

        setCitations((res.citations || []).map((citation) => {
          const [source, chunk] = citation.split('#')
          const matchedChunk = retrievalChunks.find((item) => `${item.doc_id}#${item.chunk_id}` === citation)
          return {
            id: citation,
            source: matchedChunk?.source_file || source,
            section: `Chunk ${chunk ?? '0'}`,
            text: matchedChunk?.chunk_text || '',
            relevance: matchedChunk?.score ?? 0,
          }
        }))
      })
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to generate answer')
      setGeneratedAnswer(null)
      setCitations([])
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Question Input */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Generate Answer</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Ask a question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={3}
              className="w-full p-4 border border-border rounded-md bg-bg-primary text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth resize-none"
              placeholder="Enter your question..."
            />
          </div>
          <Button variant="primary" onClick={handleGenerate} disabled={isGenerating}>
            <Send size={18} className="inline mr-2" />
            {isGenerating ? 'Generating...' : 'Generate Answer'}
          </Button>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </div>
      </Card>

      {/* Generated Answer */}
      <Card>
        <div className="mb-6 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-text-primary">Generated Answer</h3>
          {generatedAnswer ? (
            <div className="flex items-center gap-3">
              <Badge variant="success">{(generatedAnswer.confidence * 100).toFixed(0)}% Confidence</Badge>
              <span className="text-sm text-text-secondary">{generatedAnswer.generationTime}</span>
              {generatedAnswer.hallucinationRisk ? <Badge variant="warning">Review carefully</Badge> : null}
            </div>
          ) : (
            <div className="text-sm text-text-secondary">No generated answer yet</div>
          )}
        </div>

        {/* Answer Text */}
        <div className="bg-bg-primary rounded-md p-6 mb-6">
          <div className="prose prose-sm max-w-none text-text-primary leading-relaxed text-sm">
            {generatedAnswer ? (
              generatedAnswer.text.split('\n').map((line, idx) => {
                if (line.startsWith('##') || line.startsWith('**')) {
                  return (
                    <p key={idx} className="font-semibold mt-4 mb-2 text-text-primary">
                      {line.replace(/\*\*/g, '').replace(/##\s/, '')}
                    </p>
                  )
                }
                if (line.match(/^\d+\./)) {
                  return (
                    <p key={idx} className="ml-4 mb-2">
                      {line}
                    </p>
                  )
                }
                return (
                  line && (
                    <p key={idx} className="mb-3">
                      {line}
                    </p>
                  )
                )
              })
            ) : (
              <p className="text-text-secondary">No answer generated yet. Enter a question and click Generate.</p>
            )}
          </div>
        </div>

        {/* Feedback */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-text-secondary">Was this helpful?</span>
            <div className="flex gap-2">
              <button className="p-2 rounded-md hover:bg-bg-primary transition-smooth text-text-secondary hover:text-green-600">
                <ThumbsUp size={18} />
              </button>
              <button className="p-2 rounded-md hover:bg-bg-primary transition-smooth text-text-secondary hover:text-red-600">
                <ThumbsDown size={18} />
              </button>
            </div>
          </div>
          <Button variant="ghost" size="sm">
            <Copy size={18} />
            Copy Answer
          </Button>
        </div>
      </Card>

      {/* Citations */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Citations & Sources</h3>
        <div className="space-y-4">
          {citations.map((citation) => (
            <div
              key={citation.id}
              className="border border-border rounded-md p-4 hover:border-primary transition-smooth"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-text-primary">{citation.source}</p>
                  <p className="text-xs text-text-secondary">{citation.section}</p>
                </div>
                <Badge variant="info" className="text-xs">
                  {(citation.relevance * 100).toFixed(0)}% relevant
                </Badge>
              </div>
              <p className="text-sm text-text-secondary mt-2 italic">"{citation.text}"</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Suggested Refinements */}
      <Card>
        <div className="flex items-center gap-2 mb-6">
          <Lightbulb size={20} className="text-primary opacity-70" />
          <h3 className="text-lg font-semibold text-text-primary">Suggested Refinements</h3>
        </div>
        <div className="space-y-3">
          {[
            'Add comparison with competitor platforms',
            'Include pricing information',
            'Add implementation examples',
            'Mention recent feature updates',
          ].map((suggestion, idx) => (
            <div key={idx} className="flex items-center gap-3 p-3 bg-bg-primary rounded-md hover:border-primary transition-smooth cursor-pointer hover:border border border-transparent">
              <div className="w-5 h-5 rounded border border-border flex items-center justify-center"></div>
              <span className="text-sm text-text-secondary">{suggestion}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
