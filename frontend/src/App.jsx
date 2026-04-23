import { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, AlertTriangle, CheckCircle, Download, FileJson } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

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
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/mine', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError('Falha ao processar o arquivo. Verifique se o backend está rodando na porta 8000 e se o arquivo é um PDF legível.');
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    if (!results) return;
    
    const { main_document, attachments_data } = results;
    
    // Cabeçalhos
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Tipo,Data,Categoria,Valor,Descrição,Origem\n";
    
    // Documento Principal
    csvContent += `Documento Principal,${main_document.data || ''},${main_document.categoria || ''},${main_document.valor || ''},${main_document.descricao || ''},\n`;
    
    // Anexos
    attachments_data.forEach(att => {
      csvContent += `Anexo,${att.data || ''},${att.categoria || ''},${att.valor || ''},${att.descricao || ''},${att.source_link || ''}\n`;
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
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-blue-200">
      
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
        
        {/* Upload Zone */}
        {!results && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-10 flex flex-col items-center justify-center text-center transition-all">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-6 transition-all duration-500 ${loading ? 'bg-blue-100 animate-pulse' : 'bg-slate-100'}`}>
              <UploadCloud size={40} className={loading ? 'text-blue-500' : 'text-slate-400'} />
            </div>
            
            <h2 className="text-2xl font-semibold mb-2">Envie a Prestação de Contas</h2>
            <p className="text-slate-500 mb-8 max-w-md">Faça o upload do PDF principal. O motor irá minerar automaticamente o texto e baixar todos os anexos vinculados.</p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <label className="cursor-pointer group">
                <div className="flex items-center gap-2 bg-white border-2 border-dashed border-slate-300 hover:border-blue-500 px-6 py-3 rounded-xl font-medium text-slate-700 transition-colors">
                  <FileText size={20} className="text-slate-400 group-hover:text-blue-500" />
                  {file ? file.name : "Selecionar PDF"}
                </div>
                <input 
                  type="file" 
                  accept="application/pdf" 
                  onChange={handleFileChange} 
                  className="hidden" 
                />
              </label>

              <button 
                onClick={handleUpload}
                disabled={!file || loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-8 py-3.5 rounded-xl font-medium shadow-lg shadow-blue-200 transition-all flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processando...
                  </>
                ) : (
                  'Iniciar Mineração'
                )}
              </button>
            </div>
            
            {error && (
              <div className="mt-6 text-red-500 bg-red-50 px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
                <AlertTriangle size={18} />
                {error}
              </div>
            )}
          </div>
        )}

        {/* Results Area */}
        {results && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Dashboard Cards */}
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

            {/* Inconsistencies List */}
            {results.inconsistencies.length > 0 && (
              <div className="bg-white rounded-xl border border-red-200 shadow-sm overflow-hidden">
                <div className="bg-red-50 px-6 py-4 border-b border-red-100 flex items-center gap-2">
                  <AlertTriangle size={20} className="text-red-600" />
                  <h3 className="font-semibold text-red-800">Inconsistências Encontradas (RF11)</h3>
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

            {/* Data Table */}
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
                    {/* Main Doc */}
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
                    
                    {/* Attachments */}
                    {results.attachments_data.map((att, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-600 flex items-center gap-2">
                          <FileText size={16} className="text-slate-400" />
                          Anexo {idx + 1}
                        </td>
                        <td className="px-6 py-4 text-slate-600">{att.data || '-'}</td>
                        <td className="px-6 py-4">
                          <span className="bg-slate-100 border border-slate-200 px-2 py-1 rounded-md text-xs font-medium text-slate-600">{att.categoria}</span>
                        </td>
                        <td className="px-6 py-4 text-slate-600 truncate max-w-xs" title={att.descricao || ''}>{att.descricao || '-'}</td>
                        <td className="px-6 py-4 font-medium text-right text-slate-700">R$ {att.valor || '0,00'}</td>
                      </tr>
                    ))}
                    
                    {results.attachments_data.length === 0 && (
                      <tr>
                        <td colSpan="5" className="px-6 py-8 text-center text-slate-400">
                          Nenhum anexo encontrado neste documento.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="flex justify-center pt-4 pb-8">
              <button 
                onClick={() => setResults(null)}
                className="text-slate-500 hover:text-slate-800 font-medium text-sm transition-colors"
              >
                ← Analisar outro documento
              </button>
            </div>
            
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
