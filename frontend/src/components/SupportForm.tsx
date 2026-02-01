/**
 * Task T058: Support form component with React Hook Form and Zod validation
 * Requirements: FR-035 (form validation)
 *
 * Form fields:
 * - Name (required, 2-100 chars)
 * - Email (required, valid email format)
 * - Subject (required, 5-200 chars)
 * - Message (required, 10-5000 chars)
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// Validation schema using Zod (FR-035)
const supportFormSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must not exceed 100 characters'),

  email: z.string()
    .email('Please enter a valid email address')
    .min(5, 'Email is required')
    .max(255, 'Email must not exceed 255 characters'),

  subject: z.string()
    .min(5, 'Subject must be at least 5 characters')
    .max(200, 'Subject must not exceed 200 characters'),

  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message must not exceed 5000 characters'),

  priority: z.enum(['normal', 'high']).default('normal'),
});

type SupportFormData = z.infer<typeof supportFormSchema>;

interface SupportFormProps {
  onSuccess?: (ticketId: string) => void;
  onError?: (error: string) => void;
}

export default function SupportForm({ onSuccess, onError }: SupportFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [ticketId, setTicketId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportFormSchema),
    defaultValues: {
      priority: 'normal',
    },
  });

  const onSubmit = async (data: SupportFormData) => {
    setIsSubmitting(true);
    setSubmitSuccess(false);

    try {
      const response = await fetch('/api/support/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit form');
      }

      const result = await response.json();

      // Display success and ticket ID (FR-036)
      setTicketId(result.ticket_id);
      setSubmitSuccess(true);
      reset();

      if (onSuccess) {
        onSuccess(result.ticket_id);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';

      if (onError) {
        onError(errorMessage);
      }

      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess && ticketId) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-green-50 border border-green-200 rounded-lg">
        <div className="text-center">
          <div className="mb-4">
            <svg
              className="mx-auto h-12 w-12 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          <h2 className="text-2xl font-bold text-green-900 mb-2">
            Request Submitted Successfully!
          </h2>

          <p className="text-green-800 mb-4">
            Your support request has been received and is being processed.
          </p>

          <div className="bg-white border border-green-300 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-600 mb-1">Your Ticket ID:</p>
            <p className="text-xl font-mono font-bold text-gray-900">{ticketId}</p>
            <p className="text-xs text-gray-500 mt-2">
              Save this ID for tracking your request
            </p>
          </div>

          <p className="text-sm text-green-800 mb-4">
            You will receive:
            <br />
            • A confirmation email within 30 seconds
            <br />
            • A detailed response within 5 minutes
          </p>

          <button
            onClick={() => {
              setSubmitSuccess(false);
              setTicketId(null);
            }}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            Submit Another Request
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Contact Support</h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Name Field */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name <span className="text-red-500">*</span>
          </label>
          <input
            {...register('name')}
            type="text"
            id="name"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.name ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Your full name"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            {...register('email')}
            type="email"
            id="email"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.email ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="your.email@example.com"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
          )}
        </div>

        {/* Subject Field */}
        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
            Subject <span className="text-red-500">*</span>
          </label>
          <input
            {...register('subject')}
            type="text"
            id="subject"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.subject ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Brief description of your issue"
          />
          {errors.subject && (
            <p className="mt-1 text-sm text-red-600">{errors.subject.message}</p>
          )}
        </div>

        {/* Message Field */}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            Message <span className="text-red-500">*</span>
          </label>
          <textarea
            {...register('message')}
            id="message"
            rows={6}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.message ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Please describe your issue in detail..."
          />
          {errors.message && (
            <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Minimum 10 characters, maximum 5000 characters
          </p>
        </div>

        {/* Priority Field */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <select
            {...register('priority')}
            id="priority"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="normal">Normal - Response within 10 minutes</option>
            <option value="high">High - Response within 5 minutes</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Select high priority for urgent issues
          </p>
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full px-6 py-3 rounded-lg font-medium text-white transition ${
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Submitting...
              </span>
            ) : (
              'Submit Support Request'
            )}
          </button>
        </div>
      </form>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-600 text-center">
          Need immediate assistance? Email us at{' '}
          <a href="mailto:support@company.com" className="text-blue-600 hover:underline">
            support@company.com
          </a>
        </p>
      </div>
    </div>
  );
}
