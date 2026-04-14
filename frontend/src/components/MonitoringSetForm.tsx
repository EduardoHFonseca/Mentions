import React, { useState } from 'react';
import { Plus, Trash2, Send, Save, Search, CheckCircle } from 'lucide-react';

interface MonitoringRule {
  id: string;
  channel: string;
  program_name: string;
  start_time: string;
  end_time: string;
  days: number[]; // 1: Seg, 2: Ter...
}

const DAYS_OF_WEEK = [
  { id: 1, label: 'Seg' }, { id: 2, label: 'Ter' }, { id: 3, label: 'Qua' },
  { id: 4, label: 'Qui' }, { id: 5, label: 'Sex' }, { id: 6, label: 'Sáb' }, { id: 0, label: 'Dom' }
];

const MonitoringSetForm = () => {
  const [setName, setSetName] = useState('');
  const [terms, setTerms] = useState<string[]>([]);
  const [currentTerm, setCurrentTerm] = useState('');
  const [rules, setRules] = useState<MonitoringRule[]>([]);
  const [status, setStatus] = useState<'stand_by' | 'awaiting_approval'>('stand_by');

  // Adicionar Termo
  const addTerm = () => {
    if (currentTerm && !terms.includes(currentTerm)) {
      setTerms([...terms, currentTerm]);
      setCurrentTerm('');
    }
  };

  // Simular busca na Grade de Programação
  const addRuleFromGrid = () => {
    const newRule: MonitoringRule = {
      id: Math.random().toString(36).substr(2, 9),
      channel: 'Globo', // Simulado do Grid lookup
      program_name: 'Jornal Nacional', // Simulado
      start_time: '20:30',
      end_time: '21:15',
      days: [1, 2, 3, 4, 5, 6]
    };
    setRules([...rules, newRule]);
  };

  const removeRule = (id: string) => {
    setRules(rules.filter(r => r.id !== id));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-xl border border-gray-100 mt-10 font-sans">
      {/* Cabeçalho do Set */}
      <div className="mb-8 pb-6 border-b border-gray-100">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Novo Conjunto de Monitoramento</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Nome do Monitoramento</label>
            <input 
              type="text" 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Ex: Monitoramento Rural 2026"
              value={setName}
              onChange={(e) => setSetName(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Termos de Busca (Tags)</label>
            <div className="flex gap-2">
              <input 
                type="text" 
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg outline-none"
                placeholder="Pressione enter para adicionar"
                value={currentTerm}
                onChange={(e) => setCurrentTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addTerm()}
              />
              <button onClick={addTerm} className="bg-gray-100 p-2 rounded-lg hover:bg-gray-200">
                <Plus size={20} className="text-gray-600" />
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {terms.map(t => (
                <span key={t} className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-sm font-medium border border-blue-100 flex items-center gap-1">
                  {t} <button onClick={() => setTerms(terms.filter(i => i !== t))} className="hover:text-red-500">×</button>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Regras de Grade (Monitoring Rules) */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Search size={20} className="text-blue-500" /> Regras da Grade
          </h2>
          <button 
            onClick={addRuleFromGrid}
            className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
          >
            <Plus size={16} /> Consultar Grade de Programação
          </button>
        </div>

        {rules.length === 0 ? (
          <div className="text-center py-10 border-2 border-dashed border-gray-200 rounded-xl text-gray-500">
            Nenhuma regra adicionada. Consulte a grade para começar.
          </div>
        ) : (
          <div className="overflow-hidden border border-gray-200 rounded-xl">
            <table className="w-full text-left">
              <thead className="bg-gray-50 text-xs font-semibold uppercase text-gray-500">
                <tr>
                  <th className="px-4 py-3">Canal</th>
                  <th className="px-4 py-3">Programa</th>
                  <th className="px-4 py-3">Horário</th>
                  <th className="px-4 py-3">Dias</th>
                  <th className="px-4 py-3 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 font-medium text-gray-700">{rule.channel}</td>
                    <td className="px-4 py-4 text-gray-600">{rule.program_name}</td>
                    <td className="px-4 py-4 text-gray-600">{rule.start_time} - {rule.end_time}</td>
                    <td className="px-4 py-4">
                      <div className="flex gap-1">
                        {DAYS_OF_WEEK.map(d => (
                          <span key={d.id} className={`text-[10px] px-1.5 py-0.5 rounded ${rule.days.includes(d.id) ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-400'}`}>
                            {d.label}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-4 text-right">
                      <button onClick={() => removeRule(rule.id)} className="text-red-400 hover:text-red-600">
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Ações Finais */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-100">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className={`w-3 h-3 rounded-full ${status === 'stand_by' ? 'bg-yellow-400' : 'bg-blue-400 animate-pulse'}`}></span>
          Status atual: <span className="font-semibold uppercase">{status.replace('_', ' ')}</span>
        </div>
        
        <div className="flex gap-4">
          <button 
            className="flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition font-medium"
            onClick={() => setStatus('stand_by')}
          >
            <Save size={18} /> Salvar Rascunho
          </button>
          <button 
            className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium shadow-md"
            onClick={() => setStatus('awaiting_approval')}
          >
            <Send size={18} /> Enviar para Aprovação
          </button>
        </div>
      </div>
    </div>
  );
};

export default MonitoringSetForm;
