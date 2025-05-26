/**
 * Ponto de entrada principal para tipos e utilitários compartilhados
 */

// Exportar todos os tipos gerados automaticamente
export * from '../generated';

// Constantes compartilhadas
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://hubb-one-assist-front-e-back-monol-hubb-one.replit.app'
  : 'http://localhost:5000';

// Utilitários comuns
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('pt-BR');
};