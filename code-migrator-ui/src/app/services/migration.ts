import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MigrationRequest, MigrationResponse } from '../models/migration.model';

@Injectable({
  providedIn: 'root'
})
export class MigrationService {

  // FastAPI URL — where your backend is running
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  // Sends code to FastAPI, returns Observable of result
  migrate(code: string): Observable<MigrationResponse> {
    const request: MigrationRequest = { code };
    return this.http.post<MigrationResponse>(
      `${this.apiUrl}/migrate`,
      request
    );
  }

  // Gets supported languages
  getSupportedLanguages(): Observable<any> {
    return this.http.get(`${this.apiUrl}/supported-languages`);
  }
}
