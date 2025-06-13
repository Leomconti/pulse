import { BrowserRouter, Route, Routes } from 'react-router'
import { Layout } from '@/components/boilerplate'
import { ConnectionsPage } from '@/components/connections'
import NotFound from '@/app/not-found'
import { ConnectionDetailsPage } from '@/components/connection-details'
import { QueryRunnerPage } from '@/components/query-runner'
import { WorkflowPage } from '@/components/workflow'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ConnectionsPage />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/connections/:id" element={<ConnectionDetailsPage />} />
          <Route path="/query" element={<QueryRunnerPage />} />
          <Route path="/workflow" element={<WorkflowPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
