import { EvaluationQuestion } from '@/types'
import { v4 as uuidv4 } from 'uuid'

export const DEFAULT_EVALUATION_QUESTIONS: EvaluationQuestion[] = [
  { id: uuidv4(), text: 'What is the minimum attendance requirement?', category: 'Rules', expected_has_answer: true },
  { id: uuidv4(), text: 'How is CGPA calculated?', category: 'Academics', expected_has_answer: true },
  { id: uuidv4(), text: 'What are the internship eligibility criteria?', category: 'Career', expected_has_answer: true },
  { id: uuidv4(), text: 'How many marks needed to pass exams?', category: 'Rules', expected_has_answer: true },
  { id: uuidv4(), text: 'Who is the current head of computer science?', category: 'Faculty', expected_has_answer: false },
  { id: uuidv4(), text: 'What are the library timings during exam week?', category: 'Facilities', expected_has_answer: true },
  { id: uuidv4(), text: 'How do I apply for a hostel room change?', category: 'Hostel', expected_has_answer: true },
  { id: uuidv4(), text: 'Is there a fine for late fee payment?', category: 'Finance', expected_has_answer: true },
  { id: uuidv4(), text: 'What is the syllabus for the second semester physics course?', category: 'Academics', expected_has_answer: true },
  { id: uuidv4(), text: 'Can I change my elective subject after 2 weeks?', category: 'Rules', expected_has_answer: true }
]

export const SUGGESTED_QUESTIONS = [
  "What is the minimum attendance requirement?",
  "How is CGPA calculated?",
  "What are internship eligibility criteria?",
  "How many marks needed to pass exams?"
]
