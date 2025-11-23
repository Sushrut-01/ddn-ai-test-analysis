import axios from 'axios';

export const getApi = (baseUrl: string) => {
  const client = axios.create({ baseURL: baseUrl, timeout: 20000 });
  return {
    health: async () => client.get('/api/health'),
    pipeline: async () => client.get('/api/pipeline/flow'),
    analysis: async (id: string) => client.get(`/api/analysis/${id}`),
    failures: async () => client.get('/api/failures')
  };
};
