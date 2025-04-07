import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeSlug from 'rehype-slug';
import remarkGfm from 'remark-gfm';
import 'highlight.js/styles/github-dark.css';
import { cn } from '@/lib/utils';

interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export function MarkdownViewer({ content, className }: MarkdownViewerProps) {
  return (
    <div className={cn("prose prose-slate dark:prose-invert max-w-none", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeSlug]}
        components={{
          // @ts-ignore - Ignorando erros de tipagem do ReactMarkdown
          h1: ({ children, ...props }) => (
            <h1 className="text-3xl font-bold mt-6 mb-4 pb-2 border-b" {...props}>{children}</h1>
          ),
          // @ts-ignore
          h2: ({ children, ...props }) => (
            <h2 className="text-2xl font-bold mt-5 mb-3" {...props}>{children}</h2>
          ),
          // @ts-ignore
          h3: ({ children, ...props }) => (
            <h3 className="text-xl font-bold mt-4 mb-2" {...props}>{children}</h3>
          ),
          // @ts-ignore
          ul: ({ children, ...props }) => (
            <ul className="my-3 ml-6 list-disc" {...props}>{children}</ul>
          ),
          // @ts-ignore
          ol: ({ children, ...props }) => (
            <ol className="my-3 ml-6 list-decimal" {...props}>{children}</ol>
          ),
          // @ts-ignore
          li: ({ children, ...props }) => (
            <li className="my-1" {...props}>{children}</li>
          ),
          // @ts-ignore
          p: ({ children, ...props }) => (
            <p className="my-3" {...props}>{children}</p>
          ),
          // @ts-ignore
          a: ({ children, ...props }) => (
            <a className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 hover:underline" {...props}>{children}</a>
          ),
          // @ts-ignore
          code: ({ inline, className, children, ...props }) => (
            inline 
              ? <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm" {...props}>{children}</code>
              : <code className={cn("block p-4 my-4 bg-gray-100 dark:bg-gray-800 rounded-md overflow-x-auto", className)} {...props}>{children}</code>
          ),
          // @ts-ignore
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border-collapse border border-gray-300 dark:border-gray-700" {...props}>{children}</table>
            </div>
          ),
          // @ts-ignore
          th: ({ children, ...props }) => (
            <th className="border border-gray-300 dark:border-gray-700 px-4 py-2 bg-gray-100 dark:bg-gray-800 font-medium" {...props}>{children}</th>
          ),
          // @ts-ignore
          td: ({ children, ...props }) => (
            <td className="border border-gray-300 dark:border-gray-700 px-4 py-2" {...props}>{children}</td>
          ),
          // @ts-ignore
          blockquote: ({ children, ...props }) => (
            <blockquote className="pl-4 border-l-4 border-gray-300 dark:border-gray-700 my-4 italic" {...props}>{children}</blockquote>
          ),
          // @ts-ignore
          hr: (props) => (
            <hr className="my-6 border-t border-gray-300 dark:border-gray-700" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
} 