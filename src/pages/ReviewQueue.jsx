import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Badge from '../components/Badge'
import Button from '../components/Button'
import Modal from '../components/Modal'
import Progress from '../components/Progress'
import Tooltip from '../components/Tooltip'
import { useState, useEffect } from 'react'
import useSWR, { mutate } from 'swr'
import { fetchReviewQueue, approveAnswer, rejectAnswer } from '../lib/api'
import { Check, X, Edit, User, Calendar, TrendingUp, AlertCircle, Clock } from 'lucide-react'

export default function ReviewQueue() {
  const [selectedId, setSelectedId] = useState(null)
  const [filterStatus, setFilterStatus] = useState('pending')
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [reviewNotes, setReviewNotes] = useState('')
  const [rejectReason, setRejectReason] = useState('')

  const { data, error } = useSWR('/review', fetchReviewQueue, { refreshInterval: 5000 })

  const answers = data?.items || []
  const selectedAnswer = answers.find((a) => a.id === selectedId) || null
  useEffect(() => {
    if (!selectedId && answers.length) setSelectedId(answers[0].id)
  }, [answers])

  const pendingAnswers = answers.filter((a) => a.status === filterStatus)
  const highPriorityCount = answers.filter((a) => a.priority === 'high').length
  const avgReviewTime = data?.avgReviewTime || '-'
  const approvalRate = data?.approvalRate ?? '-'

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'danger'
      case 'medium':
        return 'warning'
      case 'low':
        return 'info'
      default:
        return 'default'
    }
  }

  const handleApprove = async (id) => {
    // optimistic update
    const previous = data
    try {
      mutate('/review', async (curr = previous) => {
        return {
          ...curr,
          items: curr.items.map((it) => (it.id === id ? { ...it, status: 'approved' } : it)),
        }
      }, false)
      await approveAnswer(id, { notes: reviewNotes })
      mutate('/review')
    } catch (e) {
      // rollback
      mutate('/review', previous, false)
      console.error(e)
    }
  }

  const handleReject = async (id, reason) => {
    const previous = data
    try {
      mutate('/review', async (curr = previous) => {
        return {
          ...curr,
          items: curr.items.map((it) => (it.id === id ? { ...it, status: 'rejected' } : it)),
        }
      }, false)
      await rejectAnswer(id, { reason })
      mutate('/review')
    } catch (e) {
      mutate('/review', previous, false)
      console.error(e)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">Answer Review Queue</h1>
        <p className="text-text-secondary">Review and approve AI-generated answers before publishing.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={AlertCircle}
          label="Items Pending"
          value={answers.length}
          change={`+${highPriorityCount} high priority`}
          changeType="negative"
          footer="Awaiting review"
        />
        <StatCard
          icon={Clock}
          label="Avg Review Time"
          value={avgReviewTime}
          change="-12%"
          changeType="positive"
          footer="vs last week"
        />
        <StatCard
          icon={TrendingUp}
          label="Approval Rate"
          value={`${approvalRate}%`}
          change="+2%"
          changeType="positive"
          footer="Last 30 days"
        />
      </div>

      {/* Main Review Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        {/* Queue List */}
        <Card className="lg:col-span-1 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-primary">Review Queue</h3>
            <span className="text-xs font-semibold text-text-secondary bg-bg-secondary px-2 py-1 rounded">
              {pendingAnswers.length}
            </span>
          </div>

          <div className="space-y-2">
            {pendingAnswers.map((answer) => (
              <button
                key={answer.id}
                onClick={() => setSelectedId(answer.id)}
                className={`w-full text-left p-3 rounded-lg cursor-pointer transition-smooth border ${
                  selectedId === answer.id
                    ? 'bg-secondary border-primary shadow-sm'
                    : 'bg-bg-primary border-border hover:border-primary'
                }`}
              >
                <p className="text-sm font-medium text-text-primary line-clamp-2 mb-2">
                  {answer.question}
                </p>
                <div className="flex items-center justify-between gap-2">
                  <Badge variant={getPriorityColor(answer.priority)} className="text-xs">
                    {answer.priority}
                  </Badge>
                  <span className="text-xs text-text-tertiary">{answer.submittedAt}</span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Detailed Review Panel */}
        {selectedAnswer && (
          <Card className="lg:col-span-2 flex flex-col">
            {/* Header */}
            <div className="flex items-start justify-between mb-6 pb-6 border-b border-border">
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  {selectedAnswer.question}
                </h3>
                <div className="flex items-center gap-4 flex-wrap">
                  <Tooltip content={`Submitted by ${selectedAnswer.submittedBy}`}>
                    <div className="flex items-center gap-1 text-xs text-text-secondary cursor-help">
                      <User size={14} />
                      {selectedAnswer.submittedBy}
                    </div>
                  </Tooltip>
                  <Tooltip content={selectedAnswer.submittedAt}>
                    <div className="flex items-center gap-1 text-xs text-text-secondary cursor-help">
                      <Calendar size={14} />
                      {selectedAnswer.submittedAt}
                    </div>
                  </Tooltip>
                </div>
              </div>
              <Badge variant="warning" className="text-xs">
                {selectedAnswer.status}
              </Badge>
            </div>

            {/* Quality Metrics */}
            <div className="grid grid-cols-3 gap-4 mb-6 pb-6 border-b border-border">
              <div>
                <Tooltip content="How well the answer matches the question">
                  <Progress
                    value={selectedAnswer.relevance * 100}
                    max={100}
                    label="Relevance"
                    size="sm"
                  />
                </Tooltip>
              </div>
              <div>
                <Tooltip content="Factual accuracy score">
                  <Progress
                    value={selectedAnswer.factuality * 100}
                    max={100}
                    label="Factuality"
                    size="sm"
                  />
                </Tooltip>
              </div>
              <div>
                <Tooltip content="Overall confidence level">
                  <Progress
                    value={selectedAnswer.confidence * 100}
                    max={100}
                    label="Confidence"
                    size="sm"
                  />
                </Tooltip>
              </div>
            </div>

            {/* Risk Assessment */}
            {selectedAnswer.riskScore > 0.2 && (
              <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="text-warning flex-shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="font-semibold text-warning text-sm">Risk Alert</h4>
                    <p className="text-xs text-warning opacity-75 mt-1">
                      This answer has moderate risk factors. Please review carefully before approval.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Answer Text */}
            <div className="mb-6 pb-6 border-b border-border">
              <h4 className="text-sm font-semibold text-text-primary mb-3">Answer</h4>
              <div className="bg-bg-secondary rounded-lg p-4 text-sm text-text-primary leading-relaxed border border-border">
                {selectedAnswer.answer}
              </div>
            </div>

            {/* Citations */}
            <div className="mb-6 pb-6 border-b border-border">
              <h4 className="text-sm font-semibold text-text-primary mb-3">Sources</h4>
              <div className="flex flex-wrap gap-2">
                {(selectedAnswer.citations || []).map((citation, idx) => (
                  <Tooltip key={idx} content={`Source: ${citation}`}>
                    <Badge variant="info" className="text-xs cursor-help">
                      {citation}
                    </Badge>
                  </Tooltip>
                ))}
              </div>
            </div>

            {/* Notes Section */}
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-text-primary mb-3">Review Notes</h4>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Add notes about this answer..."
                className="input-base w-full resize-none"
                rows={3}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mt-auto pt-6 border-t border-border">
              <Button
                variant="primary"
                className="flex-1 flex items-center justify-center"
                onClick={() => setShowApprovalModal(true)}
              >
                <Check size={18} className="mr-2" />
                Approve
              </Button>
              <Button
                variant="secondary"
                className="flex-1 flex items-center justify-center"
              >
                <Edit size={18} className="mr-2" />
                Edit
              </Button>
              <Button
                variant="ghost"
                className="flex-1 flex items-center justify-center text-danger hover:bg-red-50"
                onClick={() => setShowRejectModal(true)}
              >
                <X size={18} className="mr-2" />
                Reject
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Approval Modal */}
      <Modal
        isOpen={showApprovalModal}
        onClose={() => setShowApprovalModal(false)}
        title="Confirm Approval"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            Are you sure you want to approve this answer? It will be published to the knowledge base immediately.
          </p>
          <div className="bg-bg-secondary p-3 rounded-lg text-sm">
            <p className="text-text-primary font-medium">{selectedAnswer?.question}</p>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowApprovalModal(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                if (selectedAnswer) handleApprove(selectedAnswer.id)
                setShowApprovalModal(false)
              }}
            >
              Approve
            </Button>
          </div>
        </div>
      </Modal>

      {/* Reject Modal */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)}
        title="Reject Answer"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            Provide a reason for rejecting this answer so the system can improve.
          </p>
          <textarea
            placeholder="Why are you rejecting this answer?"
            className="input-base w-full resize-none"
            rows={4}
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
          />
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowRejectModal(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                if (selectedAnswer) handleReject(selectedAnswer.id, rejectReason)
                setShowRejectModal(false)
              }}
            >
              Reject
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
