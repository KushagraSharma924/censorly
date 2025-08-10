interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

class DashboardCache {
  private cache = new Map<string, CacheItem<any>>();
  private readonly DEFAULT_TTL = 2 * 60 * 1000; // 2 minutes

  set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expiry: ttl
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    if (!item) return false;

    if (Date.now() - item.timestamp > item.expiry) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  clear(): void {
    this.cache.clear();
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  // Invalidate all data when token changes or user logs out
  invalidateAll(): void {
    this.clear();
  }
}

export const dashboardCache = new DashboardCache();
