import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { FrappeUI, setConfig, frappeRequest } from 'frappe-ui';
import App from './App.vue';
import router from './router';
import './index.css';

// All client data goes through frappe-ui resources -> whitelisted endpoints.
setConfig('resourceFetcher', frappeRequest);

const app = createApp(App);
app.use(createPinia());
app.use(router);
// Point the realtime client at the site's configured socketio port (injected
// by the www/billing.html shell); frappe-ui otherwise defaults to 9000.
app.use(FrappeUI, { socketio: { port: window.socketio_port } });
app.mount('#app');
