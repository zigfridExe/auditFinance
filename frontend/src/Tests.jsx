import React, { useState } from 'react';
import axios from 'axios';
import { Cpu, FileText, Brain, Database, Calculator, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function Tests() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [testInput, setTestInput] = useState('');
  const [llmProvider, setLlmProvider] = useState('ollama'); // 'ollama' ou 'gemini'

  const runTest = async (testName) => {
    setLoading(prev => ({ ...prev, [testName]: true }));
    const startTime = performance.now();

    try {
      let response;
      switch(testName) {
        case 'llm':
          if (llmProvider === 'gemini') {
            response = await axios.post(`${API_URL}/api/test/gemini`, { prompt: testInput || 'OK' }, { timeout: 30000 });
          } else {
            const model = llmProvider === 'ollama' ? 'qwen2.5:0.5b' :
                         llmProvider === 'smol360' ? 'smollm2:360m' :
                         llmProvider === 'smol135' ? 'smollm2:135m' : 'qwen2.5:0.5b';
            response = await axios.post(`${API_URL}/api/test/ollama`, { prompt: testInput || 'OK', model }, { timeout: 50000 });
          }
          break;
        case 'ocr':
          response = await axios.post(`${API_URL}/api/test/ocr`, {}, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 65000
          });
          break;
        case 'detector':
          response = await axios.post(`${API_URL}/api/test/detector`, {}, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 15000
          });
          break;
        case 'validator':
          response = await axios.post(`${API_URL}/api/test/validator`, {
            documents: [
              { valor: 'R$ 1.500,00', data: '15/01/2026', categoria: 'Luz' },
              { valor: 'R$ 2.000,00', data: '15/01/2026', categoria: 'Água' }
            ]
          }, { timeout: 15000 });
          break;
        case 'database':
          response = await axios.get(`${API_URL}/api/test/database`, { timeout: 15000 });
          break;
        default:
          throw new Error('Teste desconhecido');
      }

      const endTime = performance.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      setResults(prev => ({
        ...prev,
        [testName]: {
          success: response.data.status === 'success' || response.data.status === 'warning',
          data: response.data,
          duration: `${duration}s`
        }
      }));
    } catch (error) {
      const endTime = performance.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      const errorMsg = error.code === 'ECONNABORTED'
        ? 'Timeout - operação demorou muito'
        : (error.response?.data?.message || error.response?.data?.detail || error.message);

      setResults(prev => ({
        ...prev,
        [testName]: {
          success: false,
          error: errorMsg,
          duration: `${duration}s`
        }
      }));
    } finally {
      setLoading(prev => ({ ...prev, [testName]: false }));
    }
  };

  const tests = [
    {
      id: 'llm',
      name: llmProvider === 'ollama' ? 'Ollama (Qwen2.5-0.5B)' :
            llmProvider === 'smol360' ? 'SmolLM2 360M' :
            llmProvider === 'smol135' ? 'SmolLM2 135M' : 'Gemini API',
      description: llmProvider === 'gemini' ? 'Testa comunicação com Gemini API' : 'Testa comunicação com LLM local',
      icon: Brain,
      color: 'purple'
    },
    {
      id: 'detector',
      name: 'Detector de Tipo PDF',
      description: 'Verifica detecção digital/escaneado',
      icon: FileText,
      color: 'blue'
    },
    {
      id: 'ocr',
      name: 'PaddleOCR',
      description: 'Testa extração de texto via OCR',
      icon: Cpu,
      color: 'orange'
    },
    {
      id: 'validator',
      name: 'Validador Matemático',
      description: 'Testa validação com Pandas',
      icon: Calculator,
      color: 'green'
    },
    {
      id: 'database',
      name: 'SQLite Database',
      description: 'Testa persistência local',
      icon: Database,
      color: 'slate'
    }
  ];

  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200 hover:border-purple-400',
    blue: 'bg-blue-50 border-blue-200 hover:border-blue-400',
    orange: 'bg-orange-50 border-orange-200 hover:border-orange-400',
    green: 'bg-green-50 border-green-200 hover:border-green-400',
    slate: 'bg-slate-50 border-slate-200 hover:border-slate-400'
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Painel de Testes do Sistema</h1>
          <p className="text-slate-600">Teste individualmente cada componente do pipeline híbrido</p>
        </div>

        {/* Seletor de motor LLM */}
        <div className="mb-6 bg-white rounded-lg border border-slate-200 p-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Motor LLM
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setLlmProvider('ollama')}
              className={`px-4 py-2 rounded-lg border ${llmProvider === 'ollama' ? 'bg-purple-100 border-purple-500' : 'bg-slate-50 border-slate-300'}`}
            >
              Ollama (Qwen2.5-0.5B)
            </button>
            <button
              onClick={() => setLlmProvider('smol360')}
              className={`px-4 py-2 rounded-lg border ${llmProvider === 'smol360' ? 'bg-purple-100 border-purple-500' : 'bg-slate-50 border-slate-300'}`}
            >
              SmolLM2 360M
            </button>
            <button
              onClick={() => setLlmProvider('smol135')}
              className={`px-4 py-2 rounded-lg border ${llmProvider === 'smol135' ? 'bg-purple-100 border-purple-500' : 'bg-slate-50 border-slate-300'}`}
            >
              SmolLM2 135M
            </button>
            <button
              onClick={() => setLlmProvider('gemini')}
              className={`px-4 py-2 rounded-lg border ${llmProvider === 'gemini' ? 'bg-purple-100 border-purple-500' : 'bg-slate-50 border-slate-300'}`}
            >
              Gemini API
            </button>
          </div>
          {llmProvider === 'gemini' && (
            <div className="mt-4 text-sm text-slate-600">
              <p>⚠️ Configure a API key no arquivo <code className="bg-slate-100 px-2 py-1 rounded">.env</code> na raiz do projeto:</p>
              <code className="bg-slate-100 px-2 py-1 rounded mt-1 block">
                GEMINI_API_KEY=sua_chave_aqui
              </code>
            </div>
          )}
          {(llmProvider === 'smol360' || llmProvider === 'smol135') && (
            <div className="mt-4 text-sm text-slate-600">
              <p>⚠️ Para usar SmolLM2, primeiro baixe o modelo no Ollama:</p>
              <code className="bg-slate-100 px-2 py-1 rounded mt-1 block">
                ollama pull smollm2:360m
              </code>
              {llmProvider === 'smol135' && (
                <code className="bg-slate-100 px-2 py-1 rounded mt-1 block">
                  ollama pull smollm2:135m
                </code>
              )}
            </div>
          )}
        </div>

        {/* Input para testes que precisam */}
        {testInput === '' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Texto de teste (para LLM)
            </label>
            <input
              type="text"
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="Digite um texto para testar o LLM..."
              className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tests.map((test) => {
            const Icon = test.icon;
            const result = results[test.id];
            const isLoading = loading[test.id];
            
            return (
              <div
                key={test.id}
                className={`bg-white rounded-xl border-2 p-6 transition-all ${colorClasses[test.color]} ${
                  isLoading ? 'animate-pulse' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-lg bg-${test.color}-100`}>
                    <Icon size={24} className={`text-${test.color}-600`} />
                  </div>
                  {result && (
                    result.success ? (
                      <CheckCircle size={20} className="text-green-500" />
                    ) : (
                      <XCircle size={20} className="text-red-500" />
                    )
                  )}
                </div>

                <h3 className="font-semibold text-lg mb-1">{test.name}</h3>
                <p className="text-sm text-slate-600 mb-4">{test.description}</p>

                <button
                  onClick={() => runTest(test.id)}
                  disabled={isLoading}
                  className="w-full bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Testando...
                    </>
                  ) : (
                    'Executar Teste'
                  )}
                </button>

                {result && (
                  <div className="mt-4 p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                      <Clock size={14} />
                      <span>Duração: {result.duration}</span>
                    </div>
                    {result.success ? (
                      <pre className="text-xs text-slate-700 overflow-auto max-h-40">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    ) : (
                      <p className="text-xs text-red-600">{result.error}</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Status do Sistema */}
        <div className="mt-8 bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-lg mb-4">Status do Sistema</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {Object.values(results).filter(r => r?.success).length}
              </p>
              <p className="text-sm text-slate-600">Testes Passando</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {Object.values(results).filter(r => r && !r.success).length}
              </p>
              <p className="text-sm text-slate-600">Testes Falhando</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-600">
                {Object.keys(results).length}
              </p>
              <p className="text-sm text-slate-600">Testes Executados</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {tests.length - Object.keys(results).length}
              </p>
              <p className="text-sm text-slate-600">Pendentes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Tests;
