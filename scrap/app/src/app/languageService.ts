import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';

@Injectable()
export class LanguageService {
    constructor(private http: HttpClient) {
    }

    getLanguageList(language: number, size: number,end:number, words: string[]) {
        const headers = new HttpHeaders();
        headers.set('Content-Type', 'application/json');
        const word = (words.join('$'));
        let req = `/query/${language}/${size}/${end}/${word}`;
        console.log(req);
        return this.http.get(req, { headers });
    }

    getModels() {
        const headers = new HttpHeaders();
        headers.set('Content-Type', 'application/json');
        return this.http.get(`/models`, { headers });
    }
}