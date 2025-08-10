class PerformanceMonitor {
  private startTimes = new Map<string, number>();

  start(operation: string): void {
    this.startTimes.set(operation, performance.now());
  }

  end(operation: string): number {
    const startTime = this.startTimes.get(operation);
    if (!startTime) {
      console.warn(`Performance: No start time found for operation "${operation}"`);
      return 0;
    }

    const duration = performance.now() - startTime;
    console.log(`Performance: ${operation} took ${duration.toFixed(2)}ms`);
    this.startTimes.delete(operation);
    return duration;
  }

  measure<T>(operation: string, fn: () => Promise<T>): Promise<T> {
    this.start(operation);
    return fn().finally(() => {
      this.end(operation);
    });
  }
}

export const perfMonitor = new PerformanceMonitor();
