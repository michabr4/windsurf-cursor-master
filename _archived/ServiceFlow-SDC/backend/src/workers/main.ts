import { Job, QueueEvents, Worker } from 'bullmq';
import { createRedisConnection, hasRedisConfig, QUEUE_NAMES } from '../queueConfig';

type JsonRecord = Record<string, unknown>;

function logJob(prefix: string, job: Job<JsonRecord>): void {
  console.log(`[worker:${prefix}] job=${job.name} id=${job.id} data=${JSON.stringify(job.data)}`);
}

async function main(): Promise<void> {
  if (!hasRedisConfig()) {
    throw new Error('REDIS_URL is required to run workers.');
  }

  const incidentConn = createRedisConnection();
  const integrationConn = createRedisConnection();
  const eventsConn = createRedisConnection();

  const incidentWorker = new Worker<JsonRecord>(
    QUEUE_NAMES.incidentEvents,
    async (job) => {
      logJob('incident-events', job);
      if (job.name === 'incident-created') {
        // Placeholder for asynchronous incident workflows:
        // - notify channels
        // - start enrichment jobs
      }
    },
    { connection: incidentConn },
  );

  const integrationWorker = new Worker<JsonRecord>(
    QUEUE_NAMES.integrationSync,
    async (job) => {
      logJob('integration-sync', job);
      if (job.name === 'tac-linked') {
        // Placeholder for TAC sync workflow:
        // - fetch TAC metadata
        // - update incident timeline
      }
    },
    { connection: integrationConn },
  );

  const events = new QueueEvents(QUEUE_NAMES.integrationSync, { connection: eventsConn });
  await events.waitUntilReady();
  events.on('failed', ({ jobId, failedReason }) => {
    console.error(`[worker:integration-sync] failed job=${jobId} reason=${failedReason}`);
  });
  events.on('completed', ({ jobId }) => {
    console.log(`[worker:integration-sync] completed job=${jobId}`);
  });

  const shutdown = async () => {
    console.log('Shutting down workers...');
    await Promise.allSettled([
      incidentWorker.close(),
      integrationWorker.close(),
      events.close(),
      incidentConn.quit(),
      integrationConn.quit(),
      eventsConn.quit(),
    ]);
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  console.log('Queue workers started.');
}

main().catch((err) => {
  console.error('Worker startup failed:', err);
  process.exit(1);
});

