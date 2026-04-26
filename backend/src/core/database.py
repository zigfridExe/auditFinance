"""
SQLite Database Manager
Persistência local de dados de auditoria financeira
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "audit_finance.db"):
        """
        Args:
            db_path: Caminho para o arquivo SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Cria conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        return conn

    def _init_db(self):
        """Inicializa as tabelas do banco"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela de documentos principais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS main_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                data TEXT,
                valor REAL,
                descricao TEXT,
                categoria TEXT,
                extraction_method TEXT,
                extraction_success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)
        
        # Tabela de anexos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                main_document_id INTEGER,
                filename TEXT NOT NULL,
                source_link TEXT,
                data TEXT,
                valor REAL,
                descricao TEXT,
                categoria TEXT,
                status TEXT,
                extraction_method TEXT,
                extraction_success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (main_document_id) REFERENCES main_documents(id)
            )
        """)
        
        # Tabela de inconsistências
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inconsistencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                main_document_id INTEGER,
                attachment_id INTEGER,
                type TEXT,
                description TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (main_document_id) REFERENCES main_documents(id),
                FOREIGN KEY (attachment_id) REFERENCES attachments(id)
            )
        """)
        
        # Índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attachments_main 
            ON attachments(main_document_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_inconsistencies_main 
            ON inconsistencies(main_document_id)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados SQLite inicializado")

    def save_main_document(self, data: Dict[str, Any], filename: str) -> int:
        """
        Salva documento principal
        
        Args:
            data: Dados extraídos do documento
            filename: Nome do arquivo
            
        Returns:
            ID do documento inserido
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO main_documents 
            (filename, data, valor, descricao, categoria, extraction_method, extraction_success, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            json.dumps(data, ensure_ascii=False),
            data.get('valor'),
            data.get('descricao'),
            data.get('categoria'),
            data.get('extraction_method'),
            data.get('extraction_success', True),
            datetime.now().isoformat()
        ))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Documento principal salvo: ID={doc_id}, filename={filename}")
        return doc_id

    def save_attachment(self, main_doc_id: int, data: Dict[str, Any]) -> int:
        """
        Salva anexo
        
        Args:
            main_doc_id: ID do documento principal
            data: Dados do anexo
            
        Returns:
            ID do anexo inserido
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO attachments 
            (main_document_id, filename, source_link, data, valor, descricao, categoria, 
             status, extraction_method, extraction_success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            main_doc_id,
            data.get('nome_arquivo'),
            data.get('source_link'),
            json.dumps(data, ensure_ascii=False),
            data.get('valor'),
            data.get('descricao'),
            data.get('categoria'),
            data.get('status'),
            data.get('extraction_method'),
            data.get('extraction_success', True)
        ))
        
        att_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Anexo salvo: ID={att_id}, main_doc_id={main_doc_id}")
        return att_id

    def save_inconsistency(self, main_doc_id: int, attachment_id: Optional[int], 
                          inconsistency: Dict[str, Any]) -> int:
        """
        Salva inconsistência
        
        Args:
            main_doc_id: ID do documento principal
            attachment_id: ID do anexo (opcional)
            inconsistency: Dados da inconsistência
            
        Returns:
            ID da inconsistência inserida
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inconsistencies 
            (main_document_id, attachment_id, type, description, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            main_doc_id,
            attachment_id,
            inconsistency.get('type'),
            inconsistency.get('description'),
            inconsistency.get('severity', 'medium')
        ))
        
        inc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Inconsistência salva: ID={inc_id}")
        return inc_id

    def get_main_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Busca documento principal por ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM main_documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_attachments(self, main_doc_id: int) -> List[Dict[str, Any]]:
        """Busca todos os anexos de um documento principal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM attachments WHERE main_document_id = ?", (main_doc_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_inconsistencies(self, main_doc_id: int) -> List[Dict[str, Any]]:
        """Busca todas as inconsistências de um documento principal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inconsistencies WHERE main_document_id = ?", (main_doc_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Busca todos os documentos principais"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM main_documents ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def delete_document(self, doc_id: int) -> bool:
        """
        Deleta documento principal e seus anexos/inconsistências
        
        Args:
            doc_id: ID do documento
            
        Returns:
            True se deletado com sucesso
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Deleta em cascata manualmente
            cursor.execute("DELETE FROM inconsistencies WHERE main_document_id = ?", (doc_id,))
            cursor.execute("DELETE FROM attachments WHERE main_document_id = ?", (doc_id,))
            cursor.execute("DELETE FROM main_documents WHERE id = ?", (doc_id,))
            
            conn.commit()
            logger.info(f"Documento {doc_id} deletado com sucesso")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao deletar documento {doc_id}: {e}")
            return False
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM main_documents")
        stats['total_documents'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attachments")
        stats['total_attachments'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inconsistencies")
        stats['total_inconsistencies'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(valor) FROM main_documents WHERE valor IS NOT NULL")
        result = cursor.fetchone()[0]
        stats['total_value'] = result if result else 0
        
        conn.close()
        
        return stats
