'use client'

import React, { useState } from 'react'
import { EvaluationRunResponse, EvaluationQuestion } from '@/types'
import { runEvaluation } from '@/lib/api'
import { DEFAULT_EVALUATION_QUESTIONS } from '@/lib/constants'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, LineChart, Line, ReferenceLine } from 'recharts'
import { Play, Activity, Clock, CheckCircle, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'

export default function EvaluationPage() {
  const [questions, setQuestions] = useState<EvaluationQuestion[]>(DEFAULT_EVALUATION_QUESTIONS)
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<EvaluationRunResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedRow, setExpandedRow] = useState<number | null>(null)

  const handleRun = async () => {
    try {
      setIsRunning(true)
      setError(null)
      setResults(null)
      const data = await runEvaluation(questions)
      setResults(data)
    } catch (err: any) {
      setError(err.message || 'Evaluation run failed')
    } finally {
      setIsRunning(false)
    }
  }

  // Formatting chart data
  const chartData = results?.results.map((r, i) => ({
    name: `Q${i + 1}`,
    basicLatency: r.basic_latency_ms,
    ragLatency: r.rag_latency_ms,
    groundedness: r.groundedness_score * 100
  })) || []

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">RAG System Evaluation</h1>
          <p className="text-gray-500 text-sm">Compare Basic LLM vs Academic RAG performance.</p>
        </div>
        <Button onClick={handleRun} isLoading={isRunning} size="lg" className="w-full sm:w-auto">
          <Play className="w-4 h-4 mr-2" /> Run Evaluation
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg flex items-start">
          <AlertTriangle className="w-5 h-5 mr-3 mt-0.5 shrink-0" />
          <div>
            <h4 className="font-semibold">Evaluation Failed</h4>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Warning banner */}
      <div className="bg-amber-50 text-amber-800 p-4 rounded-lg flex items-start text-sm">
        <Activity className="w-5 h-5 mr-3 mt-0.5 shrink-0 text-amber-600" />
        <p><strong>Note:</strong> Groundedness scores are AI-estimated metrics indicating how well the RAG answer aligns with retrieved sources. Human review is required for verifiable accuracy. The evaluation run may take 1-3 minutes depending on LLM latency.</p>
      </div>

      {results && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
          {/* Summary Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 flex flex-col justify-center items-center text-center">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Avg RAG Latency</span>
                <span className="text-2xl font-bold text-indigo-600">{Math.round(results.avg_rag_latency)} ms</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col justify-center items-center text-center">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Avg Basic Latency</span>
                <span className="text-2xl font-bold text-gray-600">{Math.round(results.avg_basic_latency)} ms</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col justify-center items-center text-center">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Avg Groundedness</span>
                <span className="text-2xl font-bold text-emerald-600">{(results.avg_groundedness * 100).toFixed(1)}%</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col justify-center items-center text-center">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Citations Success</span>
                <span className="text-2xl font-bold text-blue-600">{results.questions_with_citations} / {results.total_questions}</span>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">Latency Comparison</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <RechartsTooltip />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                    <Bar dataKey="basicLatency" name="Basic LLM" fill="#9ca3af" radius={[4,4,0,0]} />
                    <Bar dataKey="ragLatency" name="RAG" fill="#4f46e5" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">Groundedness Score (%)</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <RechartsTooltip />
                    <ReferenceLine y={70} label={{ position: 'top', value: 'Threshold', fontSize: 10, fill: '#ef4444' }} stroke="#ef4444" strokeDasharray="3 3" />
                    <Line type="monotone" dataKey="groundedness" name="Score" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Results Table */}
          <Card>
            <CardHeader className="border-b">
              <CardTitle>Detailed Results</CardTitle>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-medium">
                  <tr>
                    <th className="px-4 py-3 w-10"></th>
                    <th className="px-4 py-3">Question</th>
                    <th className="px-4 py-3 w-24">Cat</th>
                    <th className="px-4 py-3 w-32">Latency (B/R)</th>
                    <th className="px-4 py-3 w-24">Grounded</th>
                    <th className="px-4 py-3 w-24">Citations</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {results.results.map((r, i) => (
                    <React.Fragment key={i}>
                      <tr className={`hover:bg-gray-50 cursor-pointer ${expandedRow === i ? 'bg-indigo-50/50' : ''}`} onClick={() => setExpandedRow(expandedRow === i ? null : i)}>
                        <td className="px-4 py-3 text-center">
                          {expandedRow === i ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                        </td>
                        <td className="px-4 py-3 font-medium text-gray-900 truncate max-w-xs" title={r.question}>{r.question}</td>
                        <td className="px-4 py-3"><Badge variant="default" className="text-[10px]">{r.category}</Badge></td>
                        <td className="px-4 py-3 font-mono text-xs">
                          <span className="text-gray-500">{r.basic_latency_ms}</span> / <span className="text-indigo-600 font-bold">{r.rag_latency_ms}</span>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={r.groundedness_score >= 0.7 ? 'success' : r.groundedness_score > 0.4 ? 'warning' : 'danger'}>
                            {Math.round(r.groundedness_score * 100)}%
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          {r.has_citations ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <AlertTriangle className="w-4 h-4 text-amber-500" />}
                        </td>
                      </tr>
                      {expandedRow === i && (
                        <tr className="bg-gray-50 border-b border-gray-200">
                          <td colSpan={6} className="p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              <div>
                                <h5 className="font-semibold text-gray-700 text-xs uppercase mb-2">Basic LLM Response</h5>
                                <div className="bg-white border p-3 rounded-lg text-sm text-gray-600 whitespace-pre-wrap font-serif">
                                  {r.basic_llm_response || <span className="italic text-gray-400">Empty response</span>}
                                </div>
                              </div>
                              <div>
                                <h5 className="font-semibold text-indigo-700 text-xs uppercase mb-2">Academic RAG Response</h5>
                                <div className="bg-white border-indigo-100 border p-3 rounded-lg text-sm text-gray-900 whitespace-pre-wrap font-serif">
                                  {r.rag_response || <span className="italic text-gray-400">Empty response</span>}
                                </div>
                                {r.sources.length > 0 && (
                                  <div className="mt-3">
                                    <h6 className="text-xs font-semibold text-gray-500 mb-1">Sources Retrieved ({r.retrieval_count}):</h6>
                                    <ul className="text-xs text-gray-500 list-disc pl-4 space-y-1">
                                      {r.sources.slice(0, 3).map((s, idx) => (
                                        <li key={idx} className="truncate">{s.document_name} ({Math.round(s.relevance_score * 100)}%)</li>
                                      ))}
                                      {r.sources.length > 3 && <li>...and {r.sources.length - 3} more</li>}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* Dataset Preview */}
      {!results && !isRunning && (
        <Card>
          <CardHeader className="border-b bg-gray-50/50">
            <CardTitle className="text-base">Evaluation Dataset ({questions.length} questions)</CardTitle>
          </CardHeader>
          <div className="p-0">
            <ul className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
              {questions.map((q, i) => (
                <li key={q.id} className="p-4 flex items-start justify-between">
                  <div>
                    <span className="font-medium text-gray-900 text-sm">{i + 1}. {q.text}</span>
                    <div className="mt-1 flex items-center space-x-2">
                      <Badge className="text-[10px] py-0">{q.category}</Badge>
                      <span className="text-xs text-gray-500">Expected: {q.expected_has_answer ? 'Has Answer' : 'No Answer (Out of scope)'}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </Card>
      )}
    </div>
  )
}
