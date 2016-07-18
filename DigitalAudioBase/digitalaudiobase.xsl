<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="Data">
        <html>
            <head>
                <link rel="stylesheet" type="text/css">
                    <xsl:attribute name="href"><xsl:value-of select="@css"/></xsl:attribute>
                </link>
                <title>Xavier's Digital Audio Base</title>
            </head>
            <body>
                <div>
                    <p class="css-validator">
                        <a href="http://jigsaw.w3.org/css-validator/check/referer">
                            <img class="css-validator" src="http://jigsaw.w3.org/css-validator/images/vcss" alt="Valid CSS!"/>
                        </a>
                    </p>
                    <p class="top1">Digital Audio Base</p>
                    <p class="top2">by Xavier</p>
                    <div id="albums" class="albums">
                        <p class="left">albums</p>
                        <p class="right"><span class="right">skip to </span><a href="#tracks">tracks</a></p>
                        <table>
                            <tr>
                                <th class="artist">artist</th>
                                <th class="year">year</th>
                                <th class="album">album</th>
                            </tr>
                            <xsl:apply-templates select="Artist/AlbumSort" mode="header"/>
                        </table>
                    </div>
                    <div  id="tracks" class="tracks">
                        <p class="left">tracks</p>
                        <p class="right"><span class="right">back to </span><a href="#albums">albums</a></p>
                        <xsl:apply-templates/>
                    </div>
                    <p class="timestamp">
                        <xsl:value-of select="concat('Dernière mise à jour : ',@timestamp)"/>
                    </p>
                </div>
                <a href="#0" class="cd-top">Top</a>
                <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
                <script src="main.js"></script>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="AlbumSort" mode="header">
        <tr>
            <td>
                <a class="nodecoration">
                    <xsl:attribute name="href">
                        <xsl:value-of select="concat('#',../ArtistID)"/>
                    </xsl:attribute>
                    <xsl:value-of select="../@name"/>
                </a>
            </td>
            <td class="year">
                <xsl:value-of select="Year"/>
            </td>
            <td>
                <a class="nodecoration">
                    <xsl:attribute name="href">
                        <xsl:value-of select="concat('#',AlbumID)"/>
                    </xsl:attribute>
                    <xsl:value-of select="Album"/>
                </a>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="Artist[1]">
        <h2>
            <xsl:attribute name="id">
                <xsl:value-of select="ArtistID"/>
            </xsl:attribute>
            <xsl:value-of select="@name"/>
        </h2>
        <xsl:apply-templates select="AlbumSort"/>
    </xsl:template>

    <xsl:template match="Artist[position()>1]">
        <h2>
            <xsl:attribute name="id">
                <xsl:value-of select="ArtistID"/>
            </xsl:attribute>
            <xsl:value-of select="@name"/>
        </h2>
        <xsl:apply-templates select="AlbumSort"/>
    </xsl:template>

    <xsl:template match="AlbumSort">
        <h3>
            <xsl:attribute name="id">
                <xsl:value-of select="AlbumID"/>
            </xsl:attribute>
            <xsl:value-of select="Year"/> - <xsl:value-of select="Album"/>
            <img width="120" height="120" alt="No cover found!">
                <xsl:attribute name="src">
                    <xsl:value-of select="Cover"/>
                </xsl:attribute>
            </img>
        </h3>
        <xsl:if test="count(Disc[@id])>1">
            <xsl:apply-templates select="Disc"/>
        </xsl:if>
        <xsl:if test="count(Disc[@id])=1">
            <div class="listing">
                <ol>
                    <xsl:apply-templates select="Disc/Track"/>
                </ol>
            </div>
        </xsl:if>
    </xsl:template>

    <xsl:template match="Disc">
        <h5>
            CD #<xsl:value-of select="@id"/>
        </h5>
        <div class="listing">
            <ol>
                <xsl:apply-templates/>
            </ol>
        </div>
    </xsl:template>

    <xsl:template match="Track">
        <li>
            <xsl:value-of select="."/>
        </li>
    </xsl:template>

</xsl:stylesheet>
