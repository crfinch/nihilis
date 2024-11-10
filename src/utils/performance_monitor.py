import time
import logging
import psutil
from pathlib import Path
from collections import deque

class PerformanceMonitor:
	"""Monitors and logs system performance metrics."""
    
	def __init__(self, 
					window_size: int = 120,
					log_interval: int = 5,
					warning_threshold_fps: float = 55.0,
					critical_threshold_fps: float = 30.0,
					memory_warning_threshold_mb: float = 400.0,
					target_fps: int = 60,
					max_messages: int = 100):
		# print(f"Initializing PerformanceMonitor with log_interval: {log_interval}")
		self.frame_metrics = deque(maxlen=window_size)
		self.frame_count = 0
		self.last_frame_time = time.perf_counter()
		self.last_log_time = time.perf_counter()
		self.start_time = time.perf_counter()
		self.log_interval = log_interval
		self.warning_threshold_fps = warning_threshold_fps
		self.critical_threshold_fps = critical_threshold_fps
		self.memory_warning_threshold = memory_warning_threshold_mb * 1024 * 1024
		self.target_fps = target_fps
		self.max_messages = max_messages
		self.process = psutil.Process()
		
		# Set up logging
		self._setup_logging()
		self.perf_logger.info("---===Performance Monitor initialized===---")
        
	def _setup_logging(self):
		"""Set up logging with explicit configuration."""
		# Create logs directory if it doesn't exist
		log_dir = Path('logs')
		log_dir.mkdir(exist_ok=True)
		log_path = log_dir / 'performance.log'
		
		# Create logger
		self.perf_logger = logging.getLogger('performance')
		self.perf_logger.setLevel(logging.INFO)
		
		# Remove any existing handlers
		self.perf_logger.handlers = []
		
		# Create file handler
		file_handler = logging.FileHandler(log_path, mode='a')
		file_handler.setLevel(logging.INFO)
		
		# Create formatter
		formatter = logging.Formatter(
			'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
		)
		file_handler.setFormatter(formatter)
		
		# Add handler to logger
		self.perf_logger.addHandler(file_handler)
		
		# Prevent propagation to root logger
		self.perf_logger.propagate = False
		
		# print(f"Performance logging initialized. Log file: {log_path}")
        
	def start_frame(self):
		"""Start timing a new frame."""
		self.frame_start_time = time.perf_counter()
        
	def end_frame(self):
		"""End frame timing and record metrics."""
		current_time = time.perf_counter()
		frame_time = current_time - self.frame_start_time
		
		# Store individual frame metric
		self.frame_metrics.append({
			'timestamp': current_time,
			'frame_time': frame_time
		})
		self.frame_count += 1
		
		# Log performance data at intervals
		if current_time - self.last_log_time >= self.log_interval:
			self._log_performance_data()
			self.last_log_time = current_time
        
	def _log_performance_data(self):
		"""Log performance metrics."""
		if not self.frame_metrics:
			return
			
		current_time = time.perf_counter()
		
		# Calculate metrics over the logging interval
		interval_start = current_time - self.log_interval
		interval_frames = [m for m in self.frame_metrics 
							if m['timestamp'] >= interval_start]
		
		if not interval_frames:
			return
			
		# Calculate actual FPS over the interval
		num_frames = len(interval_frames)
		actual_interval = current_time - interval_frames[0]['timestamp']
		fps = num_frames / actual_interval if actual_interval > 0 else 0
		
		# Calculate average frame time
		avg_frame_time = sum(f['frame_time'] for f in interval_frames) / num_frames
		
		# Get current memory usage
		current_memory = self.process.memory_info().rss / (1024 * 1024)  # Convert to MB
		
		# Prepare log message
		log_msg = (
			f"Performance Metrics | "
			f"FPS: {fps:.1f} | "
			f"Frame Time: {avg_frame_time*1000:.1f}ms | "
			f"Memory Usage: {current_memory:.1f}MB"
		)
		
		# Add warning details if metrics are concerning
		warnings = []
		if fps < self.critical_threshold_fps:
			warnings.append(f"Critical FPS drop (target: {self.target_fps}, current: {fps:.1f})")
		elif fps < self.warning_threshold_fps:
			warnings.append(f"Low FPS (target: {self.target_fps}, current: {fps:.1f})")
		
		if warnings:
			log_msg += " | WARNING: " + "; ".join(warnings)
		
		# Log with appropriate level based on thresholds
		if fps < self.critical_threshold_fps:
			self.perf_logger.error(log_msg)
		elif fps < self.warning_threshold_fps:
			self.perf_logger.warning(log_msg)
		else:
			self.perf_logger.info(log_msg)
		for handler in self.perf_logger.handlers:
			handler.flush()
        
	def get_performance_summary(self) -> dict:
		"""Get current performance metrics for display."""
		if not self.frame_metrics:
			return {'fps': 0.0, 'frame_time': 0.0, 'memory_usage': 0.0}
			
		latest = self.frame_metrics[-1]
		return {
			'fps': latest['fps'],
			'frame_time': latest['frame_time'],
			'memory_usage': latest['memory_usage'] / (1024 * 1024)  # Convert to MB
		}