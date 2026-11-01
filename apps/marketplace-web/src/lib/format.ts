export function formatMoney(amount: string | null | undefined, currency = "GHS") {
  if (!amount) {
    return "Price unavailable";
  }
  const value = Number(amount);
  if (Number.isNaN(value)) {
    return `${currency} ${amount}`;
  }
  return new Intl.NumberFormat("en-GH", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

export function firstParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}
