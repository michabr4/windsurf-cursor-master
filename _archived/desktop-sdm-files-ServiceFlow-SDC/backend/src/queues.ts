import { Queue } from 'bullmq';
import { QUEUE_NAMES, createRedisConnection, hasRedisConfig } from './queueConfig';

type JsonRecord = Record<string, unknown>;

class QueueManager {
  private incidentQueue?: Queue<JsonRecord>;
  private integrationsQueue?: Queue<JsonRecord>;
  private enabled = false;

  init(): void {
    if (!hasRedisConfig()) {
      this.enabled = false;
      return;
    }
    const connection = createRedisConnection();
    this.incidentQueue = new Queue<JsonRecord>(QUEUE_NAMES.incidentEvents, { connection });
    this.integrationsQueue = new Queue<JsonRecord>(QUEUE_NAMES.integrationSync, { connection });
    this.enabled = true;
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  async enqueueIncidentCreated(payload: JsonRecord): Promise<void> {
    if (!this.incidentQueue) return;
    await this.incidentQueue.add('incident-created', payload, {
      removeOnComplete: 100,
      attempts: 3,
      backoff: { type: 'exponential', delay: 1000 },
    });
  }

  async enqueueTacLink(payload: JsonRecord): Promise<void> {
    if (!this.integrationsQueue) return;
    await this.integrationsQueue.add('tac-linked', payload, {
      removeOnComplete: 100,
      attempts: 3,
      backoff: { type: 'exponential', delay: 1000 },
    });
  }
}

export const queueManager = new QueueManager();

