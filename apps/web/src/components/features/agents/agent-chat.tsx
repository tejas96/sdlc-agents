'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Agent } from '@/types/api';
import { cn } from '@/lib/utils';
import { 
  PaperAirplaneIcon, 
  StopIcon,
  DocumentArrowUpIcon,
} from '@heroicons/react/24/outline';

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  metadata?: any;
}

export interface AgentChatProps {
  agent: Agent;
  onFileUpload?: (files: FileList) => void;
  className?: string;
}

const AgentChat: React.FC<AgentChatProps> = ({
  agent,
  onFileUpload,
  className,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionId, setExecutionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isExecuting) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsExecuting(true);

    try {
      // Start agent execution with streaming
      const response = await fetch(`/api/v1/agents/${agent.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          messages: [
            {
              type: 'user_input',
              content: userMessage.content,
              timestamp: userMessage.timestamp.toISOString(),
            }
          ],
          mcp_configs: {},
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle Server-Sent Events
      const eventSource = new EventSource(response.url);
      eventSourceRef.current = eventSource;
      
      let assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'claude_response' && data.data.content) {
            // Update assistant message content
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: msg.content + data.data.content }
                : msg
            ));
          } else if (data.type === 'execution_completed') {
            setIsExecuting(false);
            eventSource.close();
          } else if (data.type === 'error') {
            const errorMessage: Message = {
              id: (Date.now() + 2).toString(),
              type: 'error',
              content: `Error: ${data.message}`,
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
            setIsExecuting(false);
            eventSource.close();
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        setIsExecuting(false);
        eventSource.close();
      };

    } catch (error) {
      console.error('Error executing agent:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: 'error',
        content: `Failed to execute agent: ${error}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsExecuting(false);
    }
  };

  const handleStopExecution = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsExecuting(false);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && onFileUpload) {
      onFileUpload(files);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className={cn('flex flex-col h-[600px]', className)} variant="glass">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{agent.name}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {agent.description || `${agent.agent_type} agent`}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isExecuting}
            >
              <DocumentArrowUpIcon className="w-4 h-4 mr-2" />
              Upload Files
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileUpload}
              accept=".py,.js,.ts,.tsx,.jsx,.java,.go,.rs,.cpp,.c,.cs,.php,.rb"
            />
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full glass flex items-center justify-center">
                <svg
                  className="w-8 h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <p>Start a conversation with {agent.name}</p>
              <p className="text-xs mt-1">
                Upload files or ask questions to get started
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex',
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.type === 'user' && 'bg-primary text-primary-foreground',
                    message.type === 'assistant' && 'glass border-glass-border',
                    message.type === 'error' && 'bg-error/10 border-error/20 text-error',
                    message.type === 'system' && 'bg-muted/10 border-muted/20 text-muted-foreground'
                  )}
                >
                  <div className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </div>
                  <div className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isExecuting && (
            <div className="flex justify-start">
              <div className="glass border-glass-border rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
                  <span className="text-sm text-muted-foreground">
                    {agent.name} is thinking...
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-glass-border p-4">
          <div className="flex items-end space-x-2">
            <div className="flex-1">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask ${agent.name} a question...`}
                disabled={isExecuting}
                variant="glass"
              />
            </div>
            <div className="flex space-x-2">
              {isExecuting ? (
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={handleStopExecution}
                >
                  <StopIcon className="w-4 h-4" />
                </Button>
              ) : (
                <Button
                  variant="default"
                  size="icon"
                  onClick={handleSendMessage}
                  disabled={!input.trim()}
                >
                  <PaperAirplaneIcon className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AgentChat;
