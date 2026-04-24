import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, AlertTriangle, CheckCircle, Download, FileJson, FolderOpen, Terminal } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [workDir, setWorkDir] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Terminal state
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  // WebSocket Nativo para receber logs em tempo real
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/ws/logs');
    ws.onmessage = (event) => {
      setLogs((prev) => [...prev, event.data]);
    };
    return () => {
      ws.close();
    };
  }, []);

  // Auto-scroll do terminal
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Por favor, selecione um arquivo PDF primeiro.');
      return;
    }

    setLoading(true);
    setError(null);
    setLogs(['> Iniciando conexão com o Motor de Mineração...']);
    setResults(null);
    
    const formData = new FormData();
    formData.append('file', file);
    if (workDir) {
      formData.append('work_dir', workDir);
    }

    try {
      const response = await axios.post('http://localhost:8000/api/mine', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError('Falha ao processar o arquivo. Verifique se o backend está rodando na porta 8000.');
    } finally {
      setLoading(false);
    }
  };

  const fileInputRef = useRef(null);

  const handleMineBatch = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setLoading(true);
    setError(null);
    setLogs([`> Iniciando mineração em lote com ${files.length} arquivos selecionados...`]);
    setResults(null);
    
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('http://localhost:8000/api/mine_batch', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResults(response.data);
      }
    } catch (err) {
      console.error(err);
      setError('Falha ao enviar os arquivos da pasta selecionada. Verifique se o backend está rodando.');
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const exportCSV = () => {
    if (!results) return;
    
    const { main_document, attachments_data } = results;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Tipo,Data,Categoria,Valor,Descrição,Origem,Erro\n";
    
    const safeStr = (str) => str ? `"${str.toString().replace(/"/g, '""')}"` : '""';
    
    csvContent += `"Documento Principal",${safeStr(main_document.data)},${safeStr(main_document.categoria)},${safeStr(main_document.valor)},${safeStr(main_document.descricao)},"", ""\n`;
    
    attachments_data.forEach(att => {
      csvContent += `"Anexo",${safeStr(att.data)},${safeStr(att.categoria)},${safeStr(att.valor)},${safeStr(att.descricao)},${safeStr(att.source_link)},${safeStr(att.erro || '')}\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `extracao_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-blue-200 pb-20">
      
      {/* Header Premium */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg text-white shadow-md">
              <FileJson size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">AuditFinance</h1>
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Minerador de Contas</p>
            </div>
          </div>
          {results && (
            <button 
              onClick={exportCSV}
              className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-md font-medium text-sm transition-all shadow-sm"
            >
              <Download size={16} />
              Exportar CSV
            </button>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-8">
        
        {/* Settings & Upload Zone */}
        <div className="flex flex-col gap-8 max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 flex flex-col transition-all">
            
            <div className="mb-6 pb-6 border-b border-slate-100">
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                <FolderOpen size={18} className="text-blue-500"/>
                Processamento Direto por Pasta Local
              </label>
              <div className="flex gap-3">
                <input 
                  type="text" 
                  value={workDir}
                  onChange={(e) => setWorkDir(e.target.value)}
                  placeholder="Ex: C:\Documentos\Auditoria (Usado ao minerar PDF Principal)"
                  className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
                />
                
                <input 
                  type="file" 
                  multiple 
                  webkitdirectory="true" 
                  className="hidden" 
                  ref={fileInputRef} 
                  onChange={handleMineBatch} 
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white px-6 py-3 rounded-xl font-medium shadow-sm transition-all text-sm whitespace-nowrap flex items-center gap-2"
                >
                  <FolderOpen size={16} /> Selecionar Pasta
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-2">Você pode usar o botão verde para escolher uma pasta no seu computador e extrair todos os PDFs e notas fiscais de uma vez, sem passar pela Superlógica.</p>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50">
              <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-all duration-500 ${loading ? 'bg-blue-100 animate-pulse' : 'bg-white shadow-sm'}`}>
                <UploadCloud size={32} className={loading ? 'text-blue-500' : 'text-slate-400'} />
              </div>
              
              <h2 className="text-xl font-semibold mb-1">Selecione a Prestação</h2>
              
              <div className="mt-6 w-full flex flex-col items-center gap-3">
                <label className="cursor-pointer w-full group">
                  <div className="flex items-center justify-center gap-2 bg-white border border-slate-300 hover:border-blue-500 px-6 py-3 rounded-xl font-medium text-slate-700 transition-colors w-full">
                    <FileText size={18} className="text-slate-400 group-hover:text-blue-500" />
                    <span className="truncate max-w-[300px]">{file ? file.name : "Escolher Arquivo PDF"}</span>
                  </div>
                  <input type="file" accept="application/pdf,image/*" onChange={handleFileChange} className="hidden" />
                </label>

                <button 
                  onClick={handleUpload}
                  disabled={!file || loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-8 py-3.5 rounded-xl font-medium shadow-md transition-all flex justify-center items-center gap-2"
                >
                  {loading ? 'Processando...' : 'Iniciar Mineração'}
                </button>
              </div>
            </div>
            
            {error && (
              <div className="mt-4 text-red-500 bg-red-50 px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
                <AlertTriangle size={18} />
                {error}
              </div>
            )}
          </div>

          {/* Terminal Window */}
          {(logs.length > 0 || loading) && (
            <div className="bg-slate-900 rounded-2xl shadow-xl overflow-hidden flex flex-col h-[350px] border border-slate-800 transition-all">
              <div className="bg-slate-800 px-4 py-3 flex items-center gap-2 border-b border-slate-700">
                <Terminal size={16} className="text-emerald-400" />
                <span className="text-xs font-mono text-slate-300">minerador_engine.exe</span>
              </div>
              <div className="p-4 flex-1 overflow-y-auto font-mono text-xs sm:text-sm text-emerald-400 space-y-1">
                {logs.length === 0 ? (
                  <span className="text-slate-600">Aguardando início do processo...</span>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className="break-all">{log}</div>
                  ))
                )}
                <div ref={logsEndRef} />
              </div>
            </div>
          )}
        </div>

        {/* Results Area */}
        {results && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 mt-8 pt-8 border-t border-slate-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <p className="text-slate-500 text-sm font-medium mb-1">Status da Extração</p>
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-emerald-500" />
                  <span className="text-2xl font-bold">Concluído</span>
                </div>
              </div>
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <p className="text-slate-500 text-sm font-medium mb-1">Anexos Baixados</p>
                <div className="flex items-end gap-2">
                  <span className="text-3xl font-bold text-blue-600">{results.attachments_processed}</span>
                  <span className="text-slate-500 text-sm mb-1">de {results.attachments_found} encontrados</span>
                </div>
              </div>
              <div className={`p-6 rounded-xl border shadow-sm ${results.inconsistencies.length > 0 ? 'bg-red-50 border-red-200' : 'bg-emerald-50 border-emerald-200'}`}>
                <p className={`text-sm font-medium mb-1 ${results.inconsistencies.length > 0 ? 'text-red-700' : 'text-emerald-700'}`}>Auditoria Automática</p>
                <div className="flex items-center gap-2">
                  {results.inconsistencies.length > 0 ? (
                    <>
                      <AlertTriangle size={24} className="text-red-600" />
                      <span className="text-2xl font-bold text-red-700">{results.inconsistencies.length} Alerta(s)</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle size={24} className="text-emerald-600" />
                      <span className="text-2xl font-bold text-emerald-700">Tudo Certo</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Inconsistências */}
            {results.inconsistencies.length > 0 && (
              <div className="bg-white rounded-xl border border-red-200 shadow-sm overflow-hidden">
                <div className="bg-red-50 px-6 py-4 border-b border-red-100 flex items-center gap-2">
                  <AlertTriangle size={20} className="text-red-600" />
                  <h3 className="font-semibold text-red-800">Inconsistências Encontradas na Auditoria</h3>
                </div>
                <div className="p-6">
                  <ul className="space-y-4">
                    {results.inconsistencies.map((inc, idx) => (
                      <li key={idx} className="flex gap-4 p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <div className="bg-red-100 p-2 rounded-md h-fit">
                          <AlertTriangle size={18} className="text-red-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-800">{inc.tipo.replace('_', ' ')}</p>
                          <p className="text-slate-600 mt-1 text-sm">{inc.mensagem}</p>
                        </div>
                        <div className="ml-auto">
                          <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full">{inc.severidade}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-200">
                <h3 className="font-semibold text-slate-800">Dados Extraídos</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                      <th className="px-6 py-4 font-medium">Origem</th>
                      <th className="px-6 py-4 font-medium">Data</th>
                      <th className="px-6 py-4 font-medium">Categoria</th>
                      <th className="px-6 py-4 font-medium">Descrição</th>
                      <th className="px-6 py-4 font-medium text-right">Valor Extraído</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    <tr className="bg-blue-50/50 hover:bg-blue-50 transition-colors">
                      <td className="px-6 py-4 font-medium flex items-center gap-2 text-blue-800">
                        <FileText size={16} />
                        Doc Principal
                      </td>
                      <td className="px-6 py-4 text-slate-600">{results.main_document.data || '-'}</td>
                      <td className="px-6 py-4">
                        <span className="bg-slate-200 px-2 py-1 rounded-md text-xs font-medium text-slate-700">{results.main_document.categoria}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-600">{results.main_document.descricao || '-'}</td>
                      <td className="px-6 py-4 font-semibold text-right text-slate-800">R$ {results.main_document.valor || '0,00'}</td>
                    </tr>
                    
                    {results.attachments_data.map((att, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-blue-600 flex items-center gap-2 max-w-[200px]" title={att.nome_arquivo || `Anexo ${idx + 1}`}>
                          <FileText size={16} className="text-slate-400 shrink-0" />
                          {att.nome_arquivo ? (
                            <a href={`http://localhost:8000/archives/${encodeURIComponent(att.nome_arquivo)}`} target="_blank" rel="noreferrer" className="truncate hover:underline hover:text-blue-800">
                              {att.nome_arquivo}
                            </a>
                          ) : (
                            <span className="truncate text-slate-600">Anexo {idx + 1}</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-slate-600">{att.data || '-'}</td>
                        <td className="px-6 py-4">
                          <span className={`border px-2 py-1 rounded-md text-xs font-medium ${att.status === 'erro_leitura' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                            {att.status === 'erro_leitura' ? 'ERRO OCR/PDF' : att.categoria}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-600 truncate max-w-xs" title={att.descricao || att.erro || ''}>{att.status === 'erro_leitura' ? att.erro : (att.descricao || '-')}</td>
                        <td className="px-6 py-4 font-medium text-right text-slate-700">R$ {att.valor || '0,00'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
