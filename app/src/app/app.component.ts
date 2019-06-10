import { Component, ViewChild, ElementRef } from '@angular/core';
import { Sizes } from './languages_moc';
import { Item } from './item';
import { LanguageService } from './languageService';
import { Observable } from 'rxjs';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  @ViewChild('inputBox') input: ElementRef;

  title = 'Final Project App.';
  author = 'Camilo A. Monreal,Manuel Perez Jimenez,Pablo Bergmann Guerra';
  mail = 'kmilouh@gmail.com;manuperezj@gmail.com;bergmann.pablo@gmail.com';
  messages: Observable<string[]>;
  message = '';


  language_radioSelected: string;
  size_radioSelected: string;
  language_itemsList: Item[] = []; // Languages;
  size_itemList: Item[] = Sizes;

  modelsLanguages: Item[] = [];

  constructor(private languageService: LanguageService, private modalService: NgbModal) {
    this.language_radioSelected = '0';
    this.size_radioSelected = '5';
    languageService.getModels().subscribe(x => {
      const array = x as Item[];
      this.modelsLanguages = [];
      for (let index = 0; index < array.length; index++) {
        const element = array[index];
        this.modelsLanguages.push({ name: element.value, value: index.toString() });
      }
      this.language_itemsList = this.modelsLanguages;
    });
  }

  setFocus() {
    this.input.nativeElement.focus();
  }

  onKeydown(event) {
    if (event.key === "Enter") {
      let stringcad = this.message;
      const wordsArray = stringcad.split(/;|,| /).filter((element, index, array) => {
        return (element.trim().length > 0);
      });

      const result = this.languageService.getLanguageList(Number.parseInt(this.language_radioSelected, 10),
        Number.parseInt(this.size_radioSelected, 10), 1, wordsArray);

      result.subscribe(x => {
        const b: any = x;
        this.messages = b.items;
        console.log(this.message);
      });
    }
  }


  onselectUrl(client){
    window.open(client[0], "_blank");
  }

  open(content) {

    this.modalService.open(content, { size: 'lg' }).result.then((result) => {
      // this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      // this.closeResult = `Dismissed for ${this.getDismissReason(reason)}`;
    });
  }


}
