/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/

import React, { useState }  from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Navigation, Footer, Home, Login, Callback, Search } from "./pages";
import { getTokenFromLocalStorage,
  getUserFromLocalStorage} from './services/localStorage/localStorageService';
import { AuthProvider } from './contexts/auth.context';

import 'bootstrap/dist/css/bootstrap.min.css';
import './scss/one-page-wonder.scss';


function App() {
  const [token, setToken] = useState(getTokenFromLocalStorage);
  const [user, setUser] = useState(getUserFromLocalStorage);

    return (
    <div className="App">
      <AuthProvider
        value={{
          token,
          setToken,
          user,
          setUser,
        }}
      >
        <Router>
          <Navigation />
          <Switch>
            <Route path="/" exact component={() => <Home />} />
            <Route path="/search" exact><Search /></Route>
            <Route path="/login" exact><Login /></Route>
            <Route path="/callback" exact><Callback /></Route>
          </Switch>
          <Footer />
        </Router>
      </AuthProvider>
    </div>
  );
}

export default App;