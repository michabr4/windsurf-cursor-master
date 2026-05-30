import { useState, useEffect, useRef } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useDroppable,
  useSensor,
  useSensors,
  closestCorners,
} from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { FirewallTask, TaskStatus } from '../types'

const COLUMNS: TaskStatus[] = ['Not Started', 'In Progress', 'At Risk', 'Blocked', 'Completed']

const TOP_BORDER: Record<TaskStatus, string> = {
  'Not Started': 'border-t-slate-400',
  'In Progress': 'border-t-[#00bceb]',
  'At Risk': 'border-t-orange-400',
  'Blocked': 'border-t-red-500',
  'Completed': 'border-t-[#6cc04a]',
}

function findColumn(tasks: FirewallTask[], id: string): TaskStatus | null {
  if ((COLUMNS as string[]).includes(id)) return id as TaskStatus
  return tasks.find(t => t.id === id)?.status ?? null
}

interface CardProps {
  task: FirewallTask
  overlay?: boolean
}

function TaskCard({ task, overlay }: CardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  })
  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      {...attributes}
      {...listeners}
      className={`rounded-xl border bg-white p-3 select-none touch-none ${
        isDragging && !overlay ? 'opacity-0' : 'opacity-100'
      } ${
        overlay
          ? 'border-[#049fd9]/40 shadow-2xl rotate-1 scale-105 cursor-grabbing'
          : 'border-slate-200 shadow-sm hover:shadow-md hover:border-[#049fd9]/30 cursor-grab active:cursor-grabbing transition-all'
      }`}
    >
      <p className="text-sm font-semibold leading-snug text-slate-800">{task.name}</p>
      {task.section && (
        <p className="mt-0.5 text-xs font-medium text-[#049fd9]/80">{task.section}</p>
      )}
      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-slate-400">{task.assignee || 'Unassigned'}</span>
        {task.dueDate && <span className="text-xs text-slate-400">{task.dueDate}</span>}
      </div>
    </div>
  )
}

interface ColumnProps {
  status: TaskStatus
  tasks: FirewallTask[]
}

function Column({ status, tasks }: ColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: status })
  return (
    <div
      className={`flex-none w-64 rounded-2xl border border-t-4 bg-white shadow-sm transition-colors ${TOP_BORDER[status]} ${
        isOver ? 'border-[#049fd9]/40 bg-slate-50/80' : 'border-slate-200'
      }`}
    >
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <span className="text-sm font-semibold text-slate-700">{status}</span>
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">
          {tasks.length}
        </span>
      </div>
      <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
        <div
          ref={setNodeRef}
          className="min-h-16 max-h-[60vh] overflow-y-auto space-y-2 p-3"
        >
          {tasks.length === 0 ? (
            <p className="py-4 text-center text-xs text-slate-400">Drop tasks here</p>
          ) : (
            tasks.map(task => <TaskCard key={task.id} task={task} />)
          )}
        </div>
      </SortableContext>
    </div>
  )
}

interface Props {
  tasks: FirewallTask[]
  onTasksChange: (tasks: FirewallTask[]) => void
}

export default function KanbanBoard({ tasks, onTasksChange }: Props) {
  const [local, setLocal] = useState<FirewallTask[]>(tasks)
  const localRef = useRef(local)
  localRef.current = local

  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => { setLocal(tasks) }, [tasks])

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  )

  const handleDragStart = ({ active }: DragStartEvent) => {
    setActiveId(active.id as string)
  }

  const handleDragOver = ({ active, over }: DragOverEvent) => {
    if (!over) return
    const aid = active.id as string
    const oid = over.id as string
    if (aid === oid) return

    const prev = localRef.current
    const activeCol = findColumn(prev, aid)
    const overCol = findColumn(prev, oid)
    if (!activeCol || !overCol || activeCol === overCol) return

    setLocal(curr => {
      const activeIdx = curr.findIndex(t => t.id === aid)
      const overIdx = curr.findIndex(t => t.id === oid)
      const updated = curr.map((t, i) =>
        i === activeIdx ? { ...t, status: overCol } : t,
      )
      return overIdx >= 0 ? arrayMove(updated, activeIdx, overIdx) : updated
    })
  }

  const handleDragEnd = ({ active, over }: DragEndEvent) => {
    setActiveId(null)
    const current = localRef.current

    if (!over || active.id === over.id) {
      onTasksChange(current)
      return
    }

    const aid = active.id as string
    const oid = over.id as string
    const activeIdx = current.findIndex(t => t.id === aid)
    const overIdx = current.findIndex(t => t.id === oid)

    const result = overIdx >= 0 ? arrayMove(current, activeIdx, overIdx) : current
    setLocal(result)
    onTasksChange(result)
  }

  const activeTask = activeId ? local.find(t => t.id === activeId) : null

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4 rounded-2xl">
        {COLUMNS.map(status => (
          <Column
            key={status}
            status={status}
            tasks={local.filter(t => t.status === status)}
          />
        ))}
      </div>
      <DragOverlay dropAnimation={null}>
        {activeTask ? <TaskCard task={activeTask} overlay /> : null}
      </DragOverlay>
    </DndContext>
  )
}
