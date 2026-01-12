'use client';

import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { LLMProviderInfo } from '../types/api';

interface LLMProviderSelectorProps {
  onProviderChange?: (provider: string, providerName: string) => void;
  onError?: (error: string) => void;
}

export default function LLMProviderSelector({
  onProviderChange,
  onError,
}: LLMProviderSelectorProps) {
  const [providers, setProviders] = useState<LLMProviderInfo[]>([]);
  const [currentProvider, setCurrentProvider] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSwitching, setIsSwitching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchProviders = async () => {
    try {
      setIsLoading(true);
      const response = await api.getLLMProviders();
      setProviders(response.providers);
      setCurrentProvider(response.current);
    } catch (error) {
      onError?.(`Failed to fetch LLM providers: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderSwitch = async (providerId: string) => {
    if (providerId === currentProvider || isSwitching) return;

    const provider = providers.find(p => p.id === providerId);
    if (!provider?.configured) {
      onError?.(`${provider?.name || 'Provider'} is not configured. Please set up the required environment variables.`);
      return;
    }

    try {
      setIsSwitching(true);
      const response = await api.switchLLMProvider(providerId);
      setCurrentProvider(response.provider);
      setIsOpen(false);
      onProviderChange?.(response.provider || '', response.provider_name || '');
    } catch (error) {
      onError?.(`Failed to switch provider: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSwitching(false);
    }
  };

  const getCurrentProviderInfo = () => {
    return providers.find(p => p.id === currentProvider);
  };

  const getProviderIcon = (providerId: string) => {
    switch (providerId) {
      case 'lmstudio':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        );
      case 'gemini':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
        <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
        <span>Loading...</span>
      </div>
    );
  }

  const currentProviderInfo = getCurrentProviderInfo();

  return (
    <div className="relative" ref={dropdownRef} data-testid="llm-provider-selector">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isSwitching}
        className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
        data-testid="current-provider"
      >
        {isSwitching ? (
          <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
        ) : (
          currentProviderInfo && getProviderIcon(currentProviderInfo.id)
        )}
        <span className="text-gray-700 dark:text-gray-300">
          {currentProviderInfo?.name || 'Select Model'}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
          <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Select LLM Provider
            </p>
          </div>
          {providers.map((provider) => (
            <button
              key={provider.id}
              onClick={() => handleProviderSwitch(provider.id)}
              disabled={!provider.configured || isSwitching}
              className={`w-full flex items-start space-x-3 px-3 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left ${
                provider.id === currentProvider ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              } ${!provider.configured ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className={`mt-0.5 ${provider.id === currentProvider ? 'text-blue-500' : 'text-gray-400'}`}>
                {getProviderIcon(provider.id)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-medium ${
                    provider.id === currentProvider 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {provider.name}
                  </p>
                  {provider.id === currentProvider && (
                    <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded">
                      Active
                    </span>
                  )}
                  {!provider.configured && (
                    <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400 px-2 py-0.5 rounded">
                      Not Configured
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {provider.description}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
