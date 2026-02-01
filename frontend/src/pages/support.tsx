/**
 * Task T059: Support form page
 * Requirements: FR-035 (web form submission)
 */

import Head from 'next/head';
import SupportForm from '../components/SupportForm';

export default function SupportPage() {
  const handleSuccess = (ticketId: string) => {
    // Track successful submission (optional analytics)
    console.log('Support request submitted:', ticketId);

    // Could send to analytics service
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'support_request_submitted', {
        ticket_id: ticketId,
      });
    }
  };

  const handleError = (error: string) => {
    // Track errors (optional analytics)
    console.error('Support request error:', error);

    // Could send to error tracking service
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'support_request_error', {
        error_message: error,
      });
    }
  };

  return (
    <>
      <Head>
        <title>Contact Support - Customer Success</title>
        <meta
          name="description"
          content="Submit a support request and receive assistance from our AI-powered customer success team"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              How can we help you?
            </h1>
            <p className="text-lg text-gray-600">
              Submit your support request below and we'll get back to you within 5 minutes.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Our AI-powered support agent is available 24/7 to assist you.
            </p>
          </div>

          {/* Support Form */}
          <SupportForm onSuccess={handleSuccess} onError={handleError} />

          {/* Additional Information */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-blue-600 mb-3">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Fast Response</h3>
              <p className="text-sm text-gray-600">
                High priority requests receive responses within 5 minutes
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-blue-600 mb-3">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Secure & Private</h3>
              <p className="text-sm text-gray-600">
                Your information is encrypted and handled securely
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="text-blue-600 mb-3">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Track Progress</h3>
              <p className="text-sm text-gray-600">
                Use your ticket ID to check the status of your request
              </p>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="mt-12 bg-white p-8 rounded-lg border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Frequently Asked Questions
            </h2>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  How quickly will I receive a response?
                </h3>
                <p className="text-sm text-gray-600">
                  Normal priority requests receive responses within 10 minutes. High priority
                  requests are answered within 5 minutes. You'll also receive an immediate
                  confirmation email.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  What happens after I submit my request?
                </h3>
                <p className="text-sm text-gray-600">
                  You'll immediately receive a ticket ID for tracking. Our AI agent will process
                  your request, search our knowledge base, and send you a detailed email response.
                  If needed, your request will be escalated to our human support team.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Can I track my support request?
                </h3>
                <p className="text-sm text-gray-600">
                  Yes! Save your ticket ID and use it to check the status of your request. You'll
                  receive email updates as your request is processed.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  What if I need to speak with a human?
                </h3>
                <p className="text-sm text-gray-600">
                  Simply mention in your message that you need to speak with a human agent, and
                  your request will be escalated immediately. You can also reply to any email
                  response to reach our human support team.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
