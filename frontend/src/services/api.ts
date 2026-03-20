export interface MarkdownData {
  markdown: string;
  target: 'emulator' | 'physical';
  physical_key?: string;
}

export interface LuckyData {
  target: 'emulator' | 'physical';
  physical_key?: string;
}

const getHeaders = (apiKey: string) => ({
  'Content-Type': 'application/json',
  'X-API-Key': apiKey,
});

export const api = {
  clearEmulator: async (apiKey: string) => {
    const res = await fetch('/api/emu-clear', {
      method: 'POST',
      headers: getHeaders(apiKey),
    });
    return res.json();
  },

  printMarkdown: async (apiKey: string, data: MarkdownData) => {
    const res = await fetch('/api/print-md', {
      method: 'POST',
      headers: getHeaders(apiKey),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  luckyPrint: async (apiKey: string, data: LuckyData) => {
    const res = await fetch('/api/lucky-print', {
      method: 'POST',
      headers: getHeaders(apiKey),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  getEmulatorState: async () => {
    const res = await fetch('/api/emu-view');
    return res.json();
  },

  getPreview: async (markdown: string) => {
    const res = await fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown, target: 'emulator' }),
    });
    return res.json();
  },
};
