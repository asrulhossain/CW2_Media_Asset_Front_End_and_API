import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Login } from './components/login/login';
import { Projects } from './components/projects/projects';
import { Project } from './components/projects/project/project';

export const routes: Routes = [

    {
        path: '',
        component: Home
    },

    {
        path: 'login',
        component: Login
    },

    {
        path: 'projects',
        component: Projects
    },

        {
        path: 'projects/:id',
        component: Project
    }
];