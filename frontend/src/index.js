// src/index.js
import React from 'react';


 // Import Bootstrap CSS

import ReactDOM from 'react-dom/client'
import App from './App.js'
import './index.css'
import {persistor,store} from './redux/store.js'
import {Provider} from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import 'bootstrap/dist/css/bootstrap.min.css';
ReactDOM.createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <PersistGate persistor={persistor} loading={null}>
    <App />
    </PersistGate>
  </Provider>
 
)
