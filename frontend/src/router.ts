import Vue from 'vue';
import Router from 'vue-router';

import Home from './views/Home.vue';
import About from './views/About.vue';
import Login from './views/Login.vue';
import Users from './views/Users.vue';
import Todo from './views/Todo.vue';

import VueResource from 'vue-resource';
Vue.use(VueResource);

declare module 'vue/types/vue' {
  interface VueConstructor {
    http: VueResource.Http;
  }
}

const requestIntercept = function(request: VueResource.HttpOptions): 
VueResource.HttpInterceptor | (() => VueResource.HttpInterceptor) {
  return request.headers.set('x-access-token', localStorage.getItem('token'));
}

Vue.http.options.root = 'http://127.0.0.1:5000';
Vue.http.interceptors.push(function(request: VueResource.HttpOptions): void {
  request.headers.set('x-access-token', localStorage.getItem('token'));
});

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/users',
      name: 'users',
      component: Users,
    },
    {
      path: '/todo',
      name: 'todo',
      component: Todo,
    },
  ],
});
