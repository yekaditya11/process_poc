/**
 * Request Optimization Utilities
 * Reduces API calls through caching, debouncing, and smart batching
 */

class RequestOptimizer {
  constructor() {
    this.cache = new Map();
    this.pendingRequests = new Map();
    this.debounceTimers = new Map();
    this.requestQueue = new Map();
    
    // Configuration
    this.config = {
      cacheTimeout: 5 * 60 * 1000, // 5 minutes
      debounceDelay: 500, // 500ms
      batchTimeout: 2000, // 2 seconds
      maxCacheSize: 100
    };
    
    // Statistics
    this.stats = {
      cacheHits: 0,
      cacheMisses: 0,
      apiCallsSaved: 0,
      totalRequests: 0
    };
  }

  /**
   * Generate cache key from request parameters
   */
  generateCacheKey(url, params = {}) {
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((result, key) => {
        // Ensure null/undefined values are handled consistently
        result[key] = params[key] === null || params[key] === undefined ? null : params[key];
        return result;
      }, {});

    const cacheKey = `${url}:${JSON.stringify(sortedParams)}`;
    console.log('Generated cache key:', cacheKey);
    return cacheKey;
  }

  /**
   * Check if cached response is still valid
   */
  isCacheValid(cacheEntry) {
    return Date.now() - cacheEntry.timestamp < this.config.cacheTimeout;
  }

  /**
   * Get cached response if available and valid
   */
  getCachedResponse(cacheKey) {
    const cacheEntry = this.cache.get(cacheKey);
    
    if (!cacheEntry) {
      this.stats.cacheMisses++;
      return null;
    }
    
    if (!this.isCacheValid(cacheEntry)) {
      this.cache.delete(cacheKey);
      this.stats.cacheMisses++;
      return null;
    }
    
    this.stats.cacheHits++;
    this.stats.apiCallsSaved++;
    console.log(`Cache hit for ${cacheKey} (saved API call)`);
    return cacheEntry.data;
  }

  /**
   * Store response in cache
   */
  setCachedResponse(cacheKey, data) {
    // Implement LRU eviction if cache is full
    if (this.cache.size >= this.config.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
    
    console.log(`Cached response for ${cacheKey}`);
  }

  /**
   * Debounced API request
   */
  debouncedRequest(key, requestFn, delay = this.config.debounceDelay) {
    return new Promise((resolve, reject) => {
      // Clear existing timer
      if (this.debounceTimers.has(key)) {
        clearTimeout(this.debounceTimers.get(key));
      }
      
      // Set new timer
      const timer = setTimeout(async () => {
        try {
          const result = await requestFn();
          resolve(result);
        } catch (error) {
          reject(error);
        } finally {
          this.debounceTimers.delete(key);
        }
      }, delay);
      
      this.debounceTimers.set(key, timer);
    });
  }

  /**
   * Optimized API request with caching and deduplication
   */
  async optimizedRequest(url, options = {}) {
    this.stats.totalRequests++;

    const { params = {}, skipCache = false, ...fetchOptions } = options;
    const cacheKey = this.generateCacheKey(url, params);

    console.log('OptimizedRequest:', { url, params, skipCache, cacheKey });

    // Check cache first (unless explicitly skipped)
    if (!skipCache) {
      const cachedResponse = this.getCachedResponse(cacheKey);
      if (cachedResponse) {
        console.log('Returning cached response for:', cacheKey);
        return cachedResponse;
      }
    } else {
      console.log('Skipping cache for:', cacheKey);
    }

    // Check if same request is already pending
    if (this.pendingRequests.has(cacheKey)) {
      console.log(`Deduplicating request for ${cacheKey}`);
      return this.pendingRequests.get(cacheKey);
    }

    // Make the request
    console.log('Making fresh API request for:', cacheKey);
    const requestPromise = this.makeRequest(url, params, fetchOptions);
    this.pendingRequests.set(cacheKey, requestPromise);

    try {
      const response = await requestPromise;

      // Cache successful responses
      if (response && !skipCache) {
        this.setCachedResponse(cacheKey, response);
      }

      return response;
    } finally {
      this.pendingRequests.delete(cacheKey);
    }
  }

  /**
   * Make the actual HTTP request
   */
  async makeRequest(url, params, options) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    
    console.log(`Making API request: ${fullUrl}`);
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Batch similar requests together
   */
  batchRequest(batchKey, requestFn) {
    if (!this.requestQueue.has(batchKey)) {
      this.requestQueue.set(batchKey, []);
      
      // Process batch after timeout
      setTimeout(() => {
        const requests = this.requestQueue.get(batchKey);
        if (requests && requests.length > 0) {
          console.log(`Processing batch of ${requests.length} requests for ${batchKey}`);
          this.processBatch(batchKey, requests);
        }
        this.requestQueue.delete(batchKey);
      }, this.config.batchTimeout);
    }
    
    return new Promise((resolve, reject) => {
      this.requestQueue.get(batchKey).push({
        requestFn,
        resolve,
        reject
      });
    });
  }

  /**
   * Process batched requests
   */
  async processBatch(batchKey, requests) {
    try {
      // For now, process requests individually
      // In a real implementation, you might combine them into a single API call
      for (const request of requests) {
        try {
          const result = await request.requestFn();
          request.resolve(result);
        } catch (error) {
          request.reject(error);
        }
      }
    } catch (error) {
      // Reject all requests in batch
      requests.forEach(request => request.reject(error));
    }
  }

  /**
   * Smart data change detection
   */
  hasDataChanged(newData, cacheKey) {
    const cached = this.cache.get(cacheKey);
    if (!cached) return true;
    
    // Simple comparison - in production, you might want more sophisticated comparison
    return JSON.stringify(newData) !== JSON.stringify(cached.data);
  }

  /**
   * Clear cache for specific pattern
   */
  invalidateCache(pattern) {
    let cleared = 0;
    for (const [key] of this.cache) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
        cleared++;
      }
    }
    console.log(`Invalidated ${cleared} cache entries matching '${pattern}'`);
  }

  /**
   * Get optimization statistics
   */
  getStats() {
    const totalRequests = this.stats.cacheHits + this.stats.cacheMisses;
    const hitRate = totalRequests > 0 ? (this.stats.cacheHits / totalRequests * 100) : 0;
    
    return {
      ...this.stats,
      hitRate: Math.round(hitRate * 100) / 100,
      cacheSize: this.cache.size,
      pendingRequests: this.pendingRequests.size
    };
  }

  /**
   * Clear all caches and reset stats
   */
  reset() {
    this.cache.clear();
    this.pendingRequests.clear();
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
    this.requestQueue.clear();
    
    this.stats = {
      cacheHits: 0,
      cacheMisses: 0,
      apiCallsSaved: 0,
      totalRequests: 0
    };
    
    console.log('Request optimizer reset');
  }
}

// Create singleton instance
const requestOptimizer = new RequestOptimizer();

export default requestOptimizer;

// Export utility functions
export const {
  optimizedRequest,
  debouncedRequest,
  batchRequest,
  invalidateCache,
  getStats,
  reset
} = requestOptimizer;
