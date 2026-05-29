import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MigrationRequest, MigrationResponse } from '../models/migration.model';

@Injectable({
  providedIn: 'root'
})
export class MigrationService {


  private apiUrl = 'https://ai-code-migrator-production.up.railway.app';

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
