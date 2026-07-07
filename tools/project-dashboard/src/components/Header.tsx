interface HeaderProps {
  lastUpdated: string
}

export default function Header({ lastUpdated }: HeaderProps) {
  return (
    <header className="cisco-header px-6 py-8 text-white shadow-lg">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Factory Project Dashboard</h1>
          <p className="mt-1 text-cisco-sky">Cisco CX · SDM Platform</p>
        </div>
        <div className="inline-flex w-fit items-center rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm backdrop-blur">
          Last updated: {lastUpdated}
        </div>
      </div>
    </header>
  )
}
