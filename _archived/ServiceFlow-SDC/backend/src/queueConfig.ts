import IORedis from 'ioredis';
import { config } from './config';

export const QUEUE_NAMES = {
  incidentEvents: 'incident-events',
  integrationSync: 'integration-sync',
} as const;

export function hasRedisConfig(): boolean {
  return Boolean(config.REDIS_URL);
}

export function createRedisConnection(): IORedis {
  if (!config.REDIS_URL) {
    throw new Error('REDIS_URL is not configured');
  }
  return new IORedis(config.REDIS_URL, {
    maxRetriesPerRequest: null,
  });
}

