# server/data_collector.py
"""
完整的数据收集系统
自动记录每次仿真的输入参数和结果
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import sqlite3
import numpy as np

class SimulationDataCollector:
    def __init__(self, db_path=None):
        # 支持环境变量和容器内路径
        import os
        if db_path is None:
            db_path = os.environ.get(
                'DATABASE_PATH',
                '/data/simulation_history.db'  # Docker 容器内路径
            )

        self.db_path = db_path
        self._ensure_directory()
        self._init_database()

    def _ensure_directory(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 仿真记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                geometry_file TEXT,
                geometry_hash TEXT,
                analysis_type TEXT,
                status TEXT,
                duration REAL
            )
        ''')
        
        # 几何参数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geometry_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_id TEXT NOT NULL,
                param_name TEXT NOT NULL,
                param_value REAL NOT NULL,
                FOREIGN KEY (sim_id) REFERENCES simulations(sim_id)
            )
        ''')
        
        # 网格参数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesh_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_id TEXT NOT NULL,
                num_nodes INTEGER,
                num_elements INTEGER,
                clmax REAL,
                clmin REAL,
                mesh_quality REAL,
                FOREIGN KEY (sim_id) REFERENCES simulations(sim_id)
            )
        ''')
        
        # 结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_id TEXT NOT NULL,
                max_stress REAL,
                min_stress REAL,
                mean_stress REAL,
                max_displacement REAL,
                volume REAL,
                mass REAL,
                FOREIGN KEY (sim_id) REFERENCES simulations(sim_id)
            )
        ''')
        
        # 几何特征向量表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geometry_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_id TEXT NOT NULL,
                feature_vector BLOB NOT NULL,
                feature_dim INTEGER NOT NULL,
                FOREIGN KEY (sim_id) REFERENCES simulations(sim_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_simulation(self, geometry_file: str, analysis_type: str, 
                        geometry_params: dict = None) -> str:
        """开始新仿真，返回 sim_id"""
        
        # 生成唯一 ID
        sim_id = self._generate_sim_id(geometry_file, geometry_params)
        
        # 计算文件哈希
        geometry_hash = self._hash_file(geometry_file) if Path(geometry_file).exists() else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO simulations (sim_id, timestamp, geometry_file, 
                                       geometry_hash, analysis_type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sim_id, datetime.now().isoformat(), geometry_file, 
                 geometry_hash, analysis_type, 'running'))
            
            # 记录几何参数
            if geometry_params:
                for name, value in geometry_params.items():
                    cursor.execute('''
                        INSERT INTO geometry_params (sim_id, param_name, param_value)
                        VALUES (?, ?, ?)
                    ''', (sim_id, name, float(value)))
            
            conn.commit()
        except sqlite3.IntegrityError:
            # 已存在相同记录
            pass
        finally:
            conn.close()
        
        return sim_id
    
    def record_mesh(self, sim_id: str, mesh_info: dict):
        """记录网格信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mesh_params (sim_id, num_nodes, num_elements, 
                                    clmax, clmin, mesh_quality)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sim_id, 
              mesh_info.get('num_nodes'),
              mesh_info.get('num_elements'),
              mesh_info.get('clmax'),
              mesh_info.get('clmin'),
              mesh_info.get('quality', 0.0)))
        
        conn.commit()
        conn.close()
    
    def record_results(self, sim_id: str, results: dict):
        """记录仿真结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO results (sim_id, max_stress, min_stress, mean_stress,
                               max_displacement, volume, mass)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sim_id,
              results.get('max_stress'),
              results.get('min_stress'),
              results.get('mean_stress'),
              results.get('max_displacement'),
              results.get('volume'),
              results.get('mass')))
        
        conn.commit()
        conn.close()
    
    def record_geometry_features(self, sim_id: str, feature_vector: np.ndarray):
        """记录几何特征向量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将 numpy 数组转换为 bytes
        feature_bytes = feature_vector.tobytes()
        
        cursor.execute('''
            INSERT INTO geometry_features (sim_id, feature_vector, feature_dim)
            VALUES (?, ?, ?)
        ''', (sim_id, feature_bytes, len(feature_vector)))
        
        conn.commit()
        conn.close()
    
    def complete_simulation(self, sim_id: str, duration: float, status: str = 'completed'):
        """完成仿真记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE simulations 
            SET status = ?, duration = ?
            WHERE sim_id = ?
        ''', (status, duration, sim_id))
        
        conn.commit()
        conn.close()
    
    def get_training_data(self, analysis_type: str = None, limit: int = None):
        """获取训练数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT s.sim_id, s.analysis_type,
                   GROUP_CONCAT(gp.param_name || ':' || gp.param_value) as params,
                   mp.num_elements, mp.clmax, mp.clmin,
                   r.max_stress, r.mean_stress, r.max_displacement, r.volume
            FROM simulations s
            LEFT JOIN geometry_params gp ON s.sim_id = gp.sim_id
            LEFT JOIN mesh_params mp ON s.sim_id = mp.sim_id
            LEFT JOIN results r ON s.sim_id = r.sim_id
            WHERE s.status = 'completed'
        '''
        
        if analysis_type:
            query += f" AND s.analysis_type = '{analysis_type}'"
        
        query += " GROUP BY s.sim_id"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        
        return data
    
    def find_similar_simulations(self, geometry_hash: str, top_k: int = 5):
        """查找相似的历史仿真"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.sim_id, s.geometry_file, s.timestamp,
                   r.max_stress, r.mean_stress, r.max_displacement
            FROM simulations s
            LEFT JOIN results r ON s.sim_id = r.sim_id
            WHERE s.geometry_hash = ? AND s.status = 'completed'
            ORDER BY s.timestamp DESC
            LIMIT ?
        ''', (geometry_hash, top_k))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_statistics(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总仿真数
        cursor.execute("SELECT COUNT(*) FROM simulations")
        stats['total_simulations'] = cursor.fetchone()[0]
        
        # 成功率
        cursor.execute("SELECT COUNT(*) FROM simulations WHERE status='completed'")
        stats['successful_simulations'] = cursor.fetchone()[0]
        
        # 平均耗时
        cursor.execute("SELECT AVG(duration) FROM simulations WHERE duration IS NOT NULL")
        stats['avg_duration'] = cursor.fetchone()[0]
        
        # 按类型统计
        cursor.execute('''
            SELECT analysis_type, COUNT(*) 
            FROM simulations 
            GROUP BY analysis_type
        ''')
        stats['by_type'] = dict(cursor.fetchall())
        
        conn.close()
        
        return stats
    
    def _generate_sim_id(self, geometry_file: str, params: dict = None) -> str:
        """生成唯一 ID"""
        content = f"{geometry_file}_{datetime.now().isoformat()}"
        if params:
            content += json.dumps(params, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _hash_file(self, filepath: str) -> str:
        """计算文件哈希"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()