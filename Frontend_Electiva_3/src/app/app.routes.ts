import { Routes } from '@angular/router';
import { ListAgent } from './components/agent/list-agent/list-agent/list-agent';
import { HomeComponent } from './components/home/home-component/home-component';
import { LoginComponent } from './components/login/login-component/login-component';
import { RegisterComponent } from './components/register/register-component/register-component';
import { ReservasComponent } from './components/reservas/reservas-list/reservas-component';
import { VuelosComponent } from './components/vuelos/vuelos-list/vuelos-component';
import { EmpleadosComponent } from './components/empleados/empleados-list/empleados-component';
import { EditComponent } from './components/edit/edit-component/edit-component';
import { SaveComponent } from './components/empleados/save/save-component/save-component';
import { RecoverPasswordComponent } from './components/recoverPassword/recover-password-component/recover-password-component';
import { ReservasSave } from './components/reservas/reservas-save/reservas-save/reservas-save';
import { ReservasEdit } from './components/reservas/reservas-edit/reservas-edit/reservas-edit';
import { MantenimientoComponent } from './components/mantenimiento/mantenimiento-list/mantenimiento-component';
import { AvionList } from './components/avion/avion-list/avion-list/avion-list';
import { AvionSave } from './components/avion/save/avion-save/avion-save';
import { AvionEdit } from './components/avion/edit/avion-edit/avion-edit';

export const routes: Routes = [
    {path: 'agent', component: ListAgent},
    {path: 'login', component: LoginComponent},
    {path: '', component: HomeComponent},
    {path: 'register', component: RegisterComponent},
    {path: 'reservas', component: ReservasComponent},
    {path: 'vuelos', component: VuelosComponent},
    {path: 'empleados', component: EmpleadosComponent},
    {path: 'edit', component: EditComponent},
    {path: 'empleados-save', component: SaveComponent},
    {path: 'recoverPassword', component: RecoverPasswordComponent},
    {path: 'reservas-save', component: ReservasSave},
    {path: 'reservas-edit', component: ReservasEdit},
    {path: 'mantenimientos', component: MantenimientoComponent},
    {path: 'aviones', component: AvionList},
    {path: 'aviones-save', component: AvionSave},
    {path: 'aviones-edit', component: AvionEdit}
];
