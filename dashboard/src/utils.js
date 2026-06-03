export const money = (v, currency = '₹') =>
  `${currency} ${Number(v || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export const statusTheme = (s) =>
  ({ Paid: 'green', Open: 'blue', Overdue: 'red', Draft: 'gray', Cancelled: 'gray', Waived: 'orange' }[s] || 'gray');

export const standingTheme = (s) =>
  ({ current: 'green', past_due: 'orange', suspended: 'red' }[s] || 'gray');

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve(true);
    const s = document.createElement('script');
    s.src = src; s.onload = () => resolve(true); s.onerror = () => reject(new Error('Could not load Razorpay Checkout'));
    document.head.appendChild(s);
  });
}

// Opens the real Razorpay Checkout modal against a server-created order.
export async function openRazorpay({ key, order_id, amount, description, prefill }) {
  await loadScript('https://checkout.razorpay.com/v1/checkout.js');
  return new Promise((resolve, reject) => {
    const rzp = new window.Razorpay({
      key, order_id, amount, currency: 'INR',
      name: 'Cloud Billing', description: description || 'Payment', prefill: prefill || {},
      handler: (resp) => resolve(resp),
      modal: { ondismiss: () => reject(new Error('Payment cancelled')) },
    });
    rzp.on('payment.failed', (resp) => reject(new Error(resp.error?.description || 'Payment failed')));
    rzp.open();
  });
}

// "past_due" -> "Past Due", "current" -> "Active"
export const titleCase = (s) => {
  if (!s) return '';
  if (s === 'current') return 'Active';
  return String(s).split('_').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
};
