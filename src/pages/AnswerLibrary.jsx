import Card from '../components/Card'
import Badge from '../components/Badge'
import { Search, Filter, Tag, Eye, Copy, Trash2, Star } from 'lucide-react'
import { useState } from 'react'
import useSWR from 'swr'
import { fetchAnswerLibrary } from '../lib/api'

export default function AnswerLibrary() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTags, setSelectedTags] = useState([])
  const [favorites, setFavorites] = useState([])

  const { data } = useSWR(['/answers', searchTerm], () => fetchAnswerLibrary(searchTerm), { revalidateOnFocus: false })
  const answers = data?.items || []
  const allTags = [...new Set(answers.flatMap((answer) => answer.tags || []))]

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    )
  }

  const toggleFavorite = (id) => {
    setFavorites((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    )
  }

  const filteredAnswers = answers.filter((answer) => {
    const matchesSearch =
      !searchTerm ||
      answer.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (answer.category && answer.category.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesTags =
      selectedTags.length === 0 ||
      selectedTags.some((tag) => (answer.tags || []).includes(tag))
    return matchesSearch && matchesTags
  })

  const totalAnswers = answers.length
  const totalViews = answers.reduce((sum, a) => sum + (a.views || 0), 0)
  const avgRating = totalAnswers ? (answers.reduce((sum, a) => sum + (a.rating || 0), 0) / totalAnswers).toFixed(1) : '-'
  const stats = [
    { label: 'Total Answers', value: totalAnswers },
    { label: 'Total Views', value: totalViews },
    { label: 'Avg Rating', value: avgRating },
  ]

  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <Card key={idx}>
            <p className="text-xs text-text-secondary mb-1">{stat.label}</p>
            <p className="text-3xl font-semibold text-text-primary">{stat.value}</p>
          </Card>
        ))}
      </div>

      {/* Search & Filters */}
      <Card>
        <div className="mb-6">
          <div className="relative">
            <Search
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-text-secondary opacity-50"
              size={20}
            />
            <input
              type="text"
              placeholder="Search answers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-2 border border-border rounded-md bg-bg-primary text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth"
            />
          </div>
        </div>

        {/* Tags Filter */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Filter size={18} className="text-text-secondary" />
            <span className="text-sm font-medium text-text-secondary">Filter by tags:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {allTags.map((tag) => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-smooth ${
                  selectedTags.includes(tag)
                    ? 'bg-primary text-white'
                    : 'bg-bg-primary text-text-secondary border border-border hover:border-primary'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Answers Grid */}
      <div className="grid grid-cols-1 gap-4">
        {filteredAnswers.map((answer) => (
          <Card key={answer.id} className="hover:border-primary transition-smooth">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-base font-semibold text-text-primary mb-1">
                  {answer.question}
                </h3>
                <p className="text-xs text-text-secondary">{answer.category}</p>
              </div>
              <button
                onClick={() => toggleFavorite(answer.id)}
                className={`flex-shrink-0 p-2 rounded-md transition-smooth ${
                  favorites.includes(answer.id)
                    ? 'text-yellow-500 bg-yellow-100'
                    : 'text-text-secondary hover:bg-bg-primary'
                }`}
              >
                <Star size={20} fill={favorites.includes(answer.id) ? 'currentColor' : 'none'} />
              </button>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {(answer.tags || []).map((tag) => (
                <Badge
                  key={tag}
                  variant="default"
                  className="text-xs cursor-pointer hover:opacity-80"
                  onClick={() => toggleTag(tag)}
                >
                  <Tag size={12} className="inline mr-1" />
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Metrics */}
            <div className="flex items-center gap-6 pb-4 border-b border-border mb-4">
              <div className="flex items-center gap-2">
                <Eye size={16} className="text-text-secondary" />
                <span className="text-sm text-text-secondary">{answer.views} views</span>
              </div>
              <div className="flex items-center gap-2">
                <Star size={16} className="text-yellow-500" fill="currentColor" />
                <span className="text-sm text-text-secondary">{answer.rating}/5.0</span>
              </div>
              <div className="text-sm text-text-secondary">Updated {answer.lastUpdated}</div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button className="p-2 rounded-md hover:bg-bg-primary transition-smooth text-text-secondary hover:text-text-primary">
                <Eye size={18} />
              </button>
              <button className="p-2 rounded-md hover:bg-bg-primary transition-smooth text-text-secondary hover:text-text-primary">
                <Copy size={18} />
              </button>
              <button className="p-2 rounded-md hover:bg-bg-primary transition-smooth text-text-secondary hover:text-text-primary">
                <Trash2 size={18} />
              </button>
            </div>
          </Card>
        ))}
      </div>

      {filteredAnswers.length === 0 && (
        <Card className="text-center py-12">
          <Search className="mx-auto text-text-secondary opacity-30 mb-3" size={32} />
          <p className="text-text-secondary">No answers are available yet</p>
        </Card>
      )}
    </div>
  )
}
