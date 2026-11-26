export function Loading() {
  return <div className="status">Loading data...</div>;
}

export function ErrorBanner() {
  return (
    <div className="error-banner" role="alert">
      Data temporarily unavailable, please try again later.
    </div>
  );
}
