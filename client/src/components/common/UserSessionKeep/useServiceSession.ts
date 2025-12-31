import { useState, useEffect, useCallback } from 'react';
import { SERVICE_CONFIGS } from './sessionTypes';
import type { ServiceSessionData } from './sessionTypes';
import { getAuthToken } from '../../../lib/auth';

interface UseServiceSessionResult {
  session: ServiceSessionData | null;
  isLoading: boolean;
  error: string | null;
  archiveSession: () => Promise<boolean>;
  refreshSession: () => Promise<void>;
}

export function useServiceSession(serviceName: string): UseServiceSessionResult {
  const [session, setSession] = useState<ServiceSessionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const config = SERVICE_CONFIGS[serviceName];

  const fetchSession = useCallback(async () => {
    if (!config) {
      setError(`Unknown service: ${serviceName}`);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const token = getAuthToken();
      
      const response = await fetch(`${config.apiEndpoint}?token=${token}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          setSession(null);
          return;
        }
        throw new Error('Failed to fetch session');
      }

      const data = await response.json();
      
      if (data && data.id) {
        setSession({
          id: data.id,
          serviceName: config.serviceName,
          displayTitle: config.displayName,
          summary: config.formatSummary(data),
          updatedAt: data.updated_at || data.created_at,
          status: data.status || 'completed',
          continueUrl: config.getContinueUrl(data.id),
          metadata: data
        });
      } else {
        setSession(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setSession(null);
    } finally {
      setIsLoading(false);
    }
  }, [serviceName, config]);

  const archiveSession = useCallback(async (): Promise<boolean> => {
    if (!session || !config) return false;

    try {
      const token = getAuthToken();
      const response = await fetch(
        `${config.archiveEndpoint}/${session.id}/archive?token=${token}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        setSession(null);
        return true;
      }
      return false;
    } catch (err) {
      return false;
    }
  }, [session, config]);

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  return {
    session,
    isLoading,
    error,
    archiveSession,
    refreshSession: fetchSession
  };
}
